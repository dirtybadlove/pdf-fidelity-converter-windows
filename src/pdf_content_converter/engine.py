from __future__ import annotations

import re
import shutil
import subprocess
import tempfile
import os
from pathlib import Path
from typing import Iterable

import pypdfium2 as pdfium
from pypdf import PdfReader

from .models import (
    ConversionOptions,
    ConversionResult,
    OcrMode,
    OutputStyle,
    PageContent,
    ProgressCallback,
)
from .writers import convert_docx_to_doc, write_docx, write_epub, write_txt


class ConversionError(RuntimeError):
    """A user-actionable conversion failure."""


class MissingDependencyError(ConversionError):
    """An optional system dependency is required for the selected job."""


def find_tesseract(explicit: str | None = None) -> str | None:
    candidates = [
        explicit,
        shutil.which("tesseract"),
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    ]
    return _first_executable(candidates)


def find_word(explicit: str | None = None) -> str | None:
    candidates = [
        explicit,
        shutil.which("WINWORD.EXE"),
        *_word_registry_candidates(),
        r"C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE",
        r"C:\Program Files (x86)\Microsoft Office\root\Office16\WINWORD.EXE",
        r"C:\Program Files\Microsoft Office\Office16\WINWORD.EXE",
        r"C:\Program Files (x86)\Microsoft Office\Office16\WINWORD.EXE",
    ]
    return _first_executable(candidates)


def _word_registry_candidates() -> list[str]:
    if os.name != "nt":
        return []
    try:
        import winreg
    except ImportError:
        return []

    key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\WINWORD.EXE"
    access_modes = [winreg.KEY_READ]
    for flag_name in ("KEY_WOW64_64KEY", "KEY_WOW64_32KEY"):
        flag = getattr(winreg, flag_name, 0)
        if flag:
            access_modes.append(winreg.KEY_READ | flag)

    found: list[str] = []
    for root in (winreg.HKEY_CURRENT_USER, winreg.HKEY_LOCAL_MACHINE):
        for access in access_modes:
            try:
                with winreg.OpenKey(root, key_path, 0, access) as key:
                    value, _ = winreg.QueryValueEx(key, None)
            except OSError:
                continue
            if isinstance(value, str) and value not in found:
                found.append(value)
    return found


def _first_executable(candidates: Iterable[str | None]) -> str | None:
    for candidate in candidates:
        if not candidate:
            continue
        path = Path(candidate)
        if path.is_file():
            return str(path)
    return None


def discover_pdfs(inputs: Iterable[Path], recursive: bool = True) -> list[Path]:
    found: list[Path] = []
    seen: set[str] = set()

    for raw_path in inputs:
        path = Path(raw_path).expanduser()
        if path.is_file():
            candidates = [path] if path.suffix.lower() == ".pdf" else []
        elif path.is_dir():
            candidates = path.rglob("*") if recursive else path.glob("*")
        else:
            raise FileNotFoundError(f"输入路径不存在: {path}")

        for candidate in candidates:
            if not candidate.is_file() or candidate.suffix.lower() != ".pdf":
                continue
            resolved = candidate.resolve()
            key = str(resolved).casefold()
            if key not in seen:
                seen.add(key)
                found.append(resolved)

    return sorted(found, key=lambda item: str(item).casefold())


def convert_batch(
    sources: Iterable[Path],
    options: ConversionOptions,
    progress: ProgressCallback | None = None,
) -> list[ConversionResult]:
    options.validate()
    source_list = list(sources)
    results: list[ConversionResult] = []
    for index, source in enumerate(source_list, start=1):
        _notify(progress, f"[{index}/{len(source_list)}] 开始转换 {source.name}")
        results.append(convert_pdf(source, options, progress))
    return results


def convert_pdf(
    source: Path,
    options: ConversionOptions,
    progress: ProgressCallback | None = None,
) -> ConversionResult:
    options.validate()
    source = Path(source).resolve()
    result = ConversionResult(source=source)

    if not source.is_file() or source.suffix.lower() != ".pdf":
        result.errors["source"] = f"不是有效的 PDF 文件: {source}"
        return result

    output_folder = Path(options.output_dir).expanduser().resolve() / source.stem
    output_folder.mkdir(parents=True, exist_ok=True)

    try:
        with tempfile.TemporaryDirectory(prefix="pdf-content-converter-") as temp_name:
            temp_dir = Path(temp_name)
            pages = _extract_pages(source, temp_dir, options, progress)
            result.ocr_pages = [page.number for page in pages if page.used_ocr]

            docx_path: Path | None = None
            if "txt" in options.formats:
                _run_writer(
                    result,
                    "txt",
                    lambda: write_txt(pages, output_folder / f"{source.stem}.txt"),
                )

            if "epub" in options.formats:
                _run_writer(
                    result,
                    "epub",
                    lambda: write_epub(
                        pages,
                        output_folder / f"{source.stem}.epub",
                        source.stem,
                        options.output_style,
                    ),
                )

            if "docx" in options.formats:
                docx_path = output_folder / f"{source.stem}.docx"
                _run_writer(
                    result,
                    "docx",
                    lambda: write_docx(pages, docx_path, source.stem, options.output_style),
                )
                if "docx" not in result.outputs:
                    docx_path = None

            if "doc" in options.formats:
                word = find_word(options.word_cmd)
                if not word:
                    result.errors["doc"] = (
                        "生成真正的 .doc 需要桌面版 Microsoft Word；当前未找到 Word。"
                        "安装或修复 Microsoft 365/Office 后重新运行即可。"
                    )
                else:
                    if docx_path is None:
                        docx_path = temp_dir / f"{source.stem}.docx"
                        try:
                            write_docx(
                                pages,
                                docx_path,
                                source.stem,
                                options.output_style,
                            )
                        except Exception as exc:  # writer boundary
                            result.errors["doc"] = f"准备 DOC 中间文件失败: {exc}"
                            docx_path = None
                    if docx_path is not None:
                        _run_writer(
                            result,
                            "doc",
                            lambda: convert_docx_to_doc(
                                docx_path,
                                output_folder / f"{source.stem}.doc",
                            ),
                        )
    except Exception as exc:
        result.errors["conversion"] = str(exc)

    for output_format, output_path in result.outputs.items():
        _notify(progress, f"已生成 {output_format.upper()}: {output_path}")
    for output_format, message in result.errors.items():
        _notify(progress, f"{output_format.upper()} 未完成: {message}")
    return result


def _run_writer(result: ConversionResult, output_format: str, writer) -> None:
    try:
        result.outputs[output_format] = writer()
    except Exception as exc:  # keep independent formats independent
        result.errors[output_format] = str(exc)


def _extract_pages(
    source: Path,
    temp_dir: Path,
    options: ConversionOptions,
    progress: ProgressCallback | None,
) -> list[PageContent]:
    reader = PdfReader(str(source))
    if reader.is_encrypted:
        try:
            unlocked = reader.decrypt("")
        except Exception as exc:
            raise ConversionError("PDF 已加密，软件不会读取或请求密码。") from exc
        if not unlocked:
            raise ConversionError("PDF 已加密，软件不会读取或请求密码。")

    render_document: pdfium.PdfDocument | None = None
    tesseract: str | None = None
    pages: list[PageContent] = []
    total = len(reader.pages)
    text_is_needed = (
        "txt" in options.formats or options.output_style is OutputStyle.EDITABLE
    )

    try:
        for page_index, pdf_page in enumerate(reader.pages):
            page_number = page_index + 1
            _notify(progress, f"正在读取第 {page_number}/{total} 页")
            native_text = _extract_native_text(pdf_page) if text_is_needed else ""
            use_ocr = text_is_needed and _should_ocr(
                native_text, pdf_page, options.ocr_mode
            )
            need_image = use_ocr or options.output_style is OutputStyle.VISUAL
            image_path: Path | None = None

            if need_image:
                if render_document is None:
                    render_document = pdfium.PdfDocument(str(source))
                image_path = temp_dir / f"page-{page_number:05d}.png"
                _render_page(render_document, page_index, image_path, options.dpi)

            text = native_text
            if use_ocr:
                if tesseract is None:
                    tesseract = find_tesseract(options.tesseract_cmd)
                if not tesseract:
                    raise MissingDependencyError(
                        f"第 {page_number} 页需要 OCR，但未找到 Tesseract。"
                        "安装 Tesseract 及所选语言包后重试，或选择“不使用 OCR”。"
                    )
                _notify(progress, f"正在 OCR 第 {page_number}/{total} 页")
                text = _run_tesseract(tesseract, image_path, options.ocr_language)

            media_box = pdf_page.mediabox
            pages.append(
                PageContent(
                    number=page_number,
                    text=text,
                    width_pt=float(media_box.width),
                    height_pt=float(media_box.height),
                    image_path=image_path,
                    used_ocr=use_ocr,
                )
            )
    finally:
        if render_document is not None:
            render_document.close()

    return pages


def _extract_native_text(pdf_page) -> str:
    try:
        text = pdf_page.extract_text(extraction_mode="layout")
    except (TypeError, ValueError):
        text = pdf_page.extract_text()
    return (text or "").replace("\x00", "")


def _should_ocr(text: str, pdf_page, mode: OcrMode) -> bool:
    if mode is OcrMode.FULL:
        return True
    if mode is OcrMode.NEVER:
        return False
    visible_characters = len(re.sub(r"\s+", "", text))
    if visible_characters == 0:
        return True
    if visible_characters >= 20:
        return False
    try:
        return len(pdf_page.images) > 0
    except Exception:
        return False


def _render_page(
    document: pdfium.PdfDocument,
    page_index: int,
    destination: Path,
    dpi: int,
) -> None:
    page = document.get_page(page_index)
    bitmap = None
    image = None
    try:
        bitmap = page.render(
            scale=dpi / 72.0,
            may_draw_forms=True,
            draw_annots=True,
            fill_color=(255, 255, 255, 255),
        )
        image = bitmap.to_pil().convert("RGB")
        image.save(destination, format="PNG", optimize=True)
    finally:
        if image is not None:
            image.close()
        if bitmap is not None:
            bitmap.close()
        page.close()


def _run_tesseract(executable: str, image_path: Path | None, language: str) -> str:
    if image_path is None:
        raise ConversionError("OCR 页面图像未生成。")
    completed = subprocess.run(
        [
            executable,
            str(image_path),
            "stdout",
            "-l",
            language,
            "--psm",
            "3",
        ],
        capture_output=True,
        check=False,
        encoding="utf-8",
        errors="replace",
    )
    if completed.returncode != 0:
        detail = completed.stderr.strip() or "Tesseract 返回未知错误。"
        raise ConversionError(f"OCR 失败: {detail}")
    return completed.stdout.replace("\x0c", "").replace("\x00", "").rstrip()


def _notify(progress: ProgressCallback | None, message: str) -> None:
    if progress:
        progress(message)
