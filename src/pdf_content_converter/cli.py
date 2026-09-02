from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .engine import convert_batch, discover_pdfs
from .models import ConversionOptions, OcrMode, OutputStyle, SUPPORTED_FORMATS


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pdf-full-convert",
        description="批量将 PDF 转为 TXT、EPUB、DOCX 和 DOC。",
    )
    parser.add_argument("inputs", nargs="+", type=Path, help="PDF 文件或文件夹")
    parser.add_argument("-o", "--output", required=True, type=Path, help="输出文件夹")
    parser.add_argument(
        "-f",
        "--format",
        dest="formats",
        action="append",
        choices=SUPPORTED_FORMATS,
        help="输出格式，可重复；不指定则输出全部格式",
    )
    parser.add_argument(
        "--ocr",
        choices=[mode.value for mode in OcrMode],
        default=OcrMode.AUTO.value,
        help="auto=空文字页 OCR，full=每页 OCR，never=不 OCR",
    )
    parser.add_argument(
        "--language",
        default="chi_sim+jpn+eng",
        help="Tesseract 语言组合，例如 chi_sim+jpn+eng",
    )
    parser.add_argument(
        "--style",
        choices=[style.value for style in OutputStyle],
        default=OutputStyle.VISUAL.value,
        help="visual=原版保真固定版式，editable=可编辑文字但版式会变化",
    )
    parser.add_argument("--dpi", type=int, default=240, help="OCR/视觉模式渲染 DPI")
    parser.add_argument(
        "--no-recursive",
        action="store_true",
        help="输入文件夹时不扫描子文件夹",
    )
    parser.add_argument("--tesseract", help="tesseract 可执行文件路径")
    parser.add_argument("--word", help="Microsoft Word WINWORD.EXE 路径")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        sources = discover_pdfs(args.inputs, recursive=not args.no_recursive)
    except (FileNotFoundError, OSError) as exc:
        print(f"错误: {exc}", file=sys.stderr)
        return 2
    if not sources:
        print("错误: 没有找到 PDF 文件。", file=sys.stderr)
        return 2

    options = ConversionOptions(
        output_dir=args.output,
        formats=tuple(args.formats or SUPPORTED_FORMATS),
        ocr_mode=OcrMode(args.ocr),
        ocr_language=args.language,
        output_style=OutputStyle(args.style),
        dpi=args.dpi,
        recursive=not args.no_recursive,
        tesseract_cmd=args.tesseract,
        word_cmd=args.word,
    )
    try:
        results = convert_batch(sources, options, progress=print)
    except ValueError as exc:
        print(f"错误: {exc}", file=sys.stderr)
        return 2

    failed = False
    print("\n转换汇总")
    for result in results:
        print(f"- {result.source.name}")
        for output_format, output_path in result.outputs.items():
            print(f"  {output_format.upper()}: {output_path}")
        for output_format, message in result.errors.items():
            failed = True
            print(f"  {output_format.upper()} 失败: {message}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
