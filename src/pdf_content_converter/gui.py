from __future__ import annotations

import os
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from .engine import convert_batch, discover_pdfs, find_tesseract, find_word
from .models import ConversionOptions, OcrMode, OutputStyle, SUPPORTED_FORMATS


OCR_LABELS = {
    "智能识别（推荐）": OcrMode.AUTO,
    "每一页都 OCR": OcrMode.FULL,
    "不使用 OCR": OcrMode.NEVER,
}

STYLE_LABELS = {
    "原版保真固定版式（推荐）": OutputStyle.VISUAL,
    "可编辑文字（会改变版式）": OutputStyle.EDITABLE,
}


def default_output_dir() -> Path:
    return Path.home() / "Desktop"


class ConverterApp(ttk.Frame):
    def __init__(self, master: tk.Tk) -> None:
        super().__init__(master, padding=18)
        self.master = master
        self.input_paths: list[Path] = []
        self.output_var = tk.StringVar(value=str(default_output_dir()))
        self.ocr_var = tk.StringVar(value="智能识别（推荐）")
        self.style_var = tk.StringVar(value="原版保真固定版式（推荐）")
        self.language_var = tk.StringVar(value="chi_sim+jpn+eng")
        self.recursive_var = tk.BooleanVar(value=True)
        self.format_vars = {
            "txt": tk.BooleanVar(value=False),
            "epub": tk.BooleanVar(value=True),
            "docx": tk.BooleanVar(value=True),
            "doc": tk.BooleanVar(value=find_word() is not None),
        }
        self.status_var = tk.StringVar(value="请选择 PDF 文件或文件夹。")
        self._build()

    def _build(self) -> None:
        self.master.title("PDF 原版保真转换器")
        self.master.minsize(820, 650)
        self.grid(sticky="nsew")
        self.master.columnconfigure(0, weight=1)
        self.master.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        title = ttk.Label(self, text="PDF 原版保真转换器", font=("Microsoft YaHei UI", 18, "bold"))
        title.grid(row=0, column=0, sticky="w")
        subtitle = ttk.Label(
            self,
            text="源 PDF 只读；默认将完整页面原样保存到移动端 EPUB 和 Word。",
        )
        subtitle.grid(row=1, column=0, sticky="w", pady=(4, 14))

        source_box = ttk.LabelFrame(self, text="1. 选择来源", padding=10)
        source_box.grid(row=2, column=0, sticky="nsew")
        source_box.columnconfigure(0, weight=1)
        source_box.rowconfigure(1, weight=1)
        button_row = ttk.Frame(source_box)
        button_row.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        ttk.Button(button_row, text="添加 PDF", command=self._add_files).pack(side="left")
        ttk.Button(button_row, text="添加文件夹", command=self._add_folder).pack(side="left", padx=8)
        ttk.Button(button_row, text="清空", command=self._clear_inputs).pack(side="left")
        ttk.Checkbutton(
            button_row,
            text="扫描子文件夹",
            variable=self.recursive_var,
        ).pack(side="right")

        self.input_list = tk.Listbox(source_box, height=8, selectmode=tk.EXTENDED)
        self.input_list.grid(row=1, column=0, sticky="nsew")

        options_box = ttk.LabelFrame(self, text="2. 输出设置", padding=10)
        options_box.grid(row=3, column=0, sticky="ew", pady=12)
        options_box.columnconfigure(1, weight=1)

        ttk.Label(options_box, text="输出文件夹").grid(row=0, column=0, sticky="w")
        ttk.Entry(options_box, textvariable=self.output_var).grid(
            row=0, column=1, sticky="ew", padx=8
        )
        ttk.Button(options_box, text="选择", command=self._choose_output).grid(row=0, column=2)

        ttk.Label(options_box, text="格式").grid(row=1, column=0, sticky="w", pady=(10, 0))
        format_row = ttk.Frame(options_box)
        format_row.grid(row=1, column=1, columnspan=2, sticky="w", pady=(10, 0))
        for output_format in SUPPORTED_FORMATS:
            ttk.Checkbutton(
                format_row,
                text=output_format.upper(),
                variable=self.format_vars[output_format],
            ).pack(side="left", padx=(0, 14))

        ttk.Label(options_box, text="识别方式").grid(row=2, column=0, sticky="w", pady=(10, 0))
        ttk.Combobox(
            options_box,
            textvariable=self.ocr_var,
            values=list(OCR_LABELS),
            state="readonly",
        ).grid(row=2, column=1, sticky="ew", padx=8, pady=(10, 0))

        ttk.Label(options_box, text="OCR 语言").grid(row=3, column=0, sticky="w", pady=(10, 0))
        ttk.Entry(options_box, textvariable=self.language_var).grid(
            row=3, column=1, sticky="ew", padx=8, pady=(10, 0)
        )
        ttk.Label(options_box, text="例如：chi_sim+jpn+eng").grid(
            row=3, column=2, sticky="w", pady=(10, 0)
        )

        ttk.Label(options_box, text="版式模式").grid(
            row=4, column=0, sticky="w", pady=(10, 0)
        )
        ttk.Combobox(
            options_box,
            textvariable=self.style_var,
            values=list(STYLE_LABELS),
            state="readonly",
        ).grid(row=4, column=1, columnspan=2, sticky="ew", padx=8, pady=(10, 0))

        ttk.Label(
            options_box,
            text="保真模式会保留每页的文字位置、表格、图片和页序；内容以整页图像保存，不可编辑。",
            wraplength=680,
        ).grid(row=5, column=0, columnspan=3, sticky="w", pady=(10, 0))

        dependency_text = (
            f"Tesseract OCR：{'已找到' if find_tesseract() else '未安装'}    "
            f"Microsoft Word（DOC）：{'已找到' if find_word() else '未安装'}"
        )
        ttk.Label(options_box, text=dependency_text).grid(
            row=6, column=0, columnspan=3, sticky="w", pady=(10, 0)
        )

        action_box = ttk.Frame(self)
        action_box.grid(row=4, column=0, sticky="ew")
        action_box.columnconfigure(0, weight=1)
        self.progress = ttk.Progressbar(action_box, mode="indeterminate")
        self.progress.grid(row=0, column=0, sticky="ew", padx=(0, 12))
        self.start_button = ttk.Button(action_box, text="开始转换", command=self._start)
        self.start_button.grid(row=0, column=1)
        ttk.Button(action_box, text="打开输出文件夹", command=self._open_output).grid(
            row=0, column=2, padx=(8, 0)
        )

        ttk.Label(self, textvariable=self.status_var, wraplength=780).grid(
            row=5, column=0, sticky="w", pady=(10, 0)
        )

    def _add_files(self) -> None:
        names = filedialog.askopenfilenames(
            title="选择 PDF",
            filetypes=[("PDF 文件", "*.pdf")],
        )
        self._append_inputs(Path(name) for name in names)

    def _add_folder(self) -> None:
        name = filedialog.askdirectory(title="选择包含 PDF 的文件夹")
        if name:
            self._append_inputs([Path(name)])

    def _append_inputs(self, paths) -> None:
        existing = {str(path.resolve()).casefold() for path in self.input_paths}
        for path in paths:
            resolved = path.resolve()
            key = str(resolved).casefold()
            if key not in existing:
                existing.add(key)
                self.input_paths.append(resolved)
                self.input_list.insert(tk.END, str(resolved))
        if self.input_paths:
            self.status_var.set(f"已选择 {len(self.input_paths)} 个来源。")

    def _clear_inputs(self) -> None:
        self.input_paths.clear()
        self.input_list.delete(0, tk.END)
        self.status_var.set("请选择 PDF 文件或文件夹。")

    def _choose_output(self) -> None:
        name = filedialog.askdirectory(title="选择输出文件夹")
        if name:
            self.output_var.set(name)

    def _start(self) -> None:
        if not self.input_paths:
            messagebox.showwarning("缺少来源", "请先添加 PDF 文件或文件夹。")
            return
        formats = tuple(
            output_format
            for output_format, variable in self.format_vars.items()
            if variable.get()
        )
        if not formats:
            messagebox.showwarning("缺少格式", "请至少选择一种输出格式。")
            return

        try:
            sources = discover_pdfs(self.input_paths, recursive=self.recursive_var.get())
        except Exception as exc:
            messagebox.showerror("无法读取来源", str(exc))
            return
        if not sources:
            messagebox.showwarning("没有 PDF", "所选来源中没有找到 PDF 文件。")
            return

        options = ConversionOptions(
            output_dir=Path(self.output_var.get()),
            formats=formats,
            ocr_mode=OCR_LABELS[self.ocr_var.get()],
            ocr_language=self.language_var.get().strip(),
            output_style=STYLE_LABELS[self.style_var.get()],
            recursive=self.recursive_var.get(),
        )
        try:
            options.validate()
        except ValueError as exc:
            messagebox.showerror("设置有误", str(exc))
            return

        self.start_button.configure(state="disabled")
        self.progress.start(10)
        self.status_var.set(f"准备转换 {len(sources)} 个 PDF……")
        threading.Thread(
            target=self._worker,
            args=(sources, options),
            daemon=True,
        ).start()

    def _worker(self, sources: list[Path], options: ConversionOptions) -> None:
        try:
            results = convert_batch(sources, options, self._thread_progress)
            self.after(0, self._finished, results, options.output_dir)
        except Exception as exc:
            self.after(0, self._failed, str(exc))

    def _thread_progress(self, message: str) -> None:
        self.after(0, self.status_var.set, message)

    def _finished(self, results, output_dir: Path) -> None:
        self.progress.stop()
        self.start_button.configure(state="normal")
        output_count = sum(len(result.outputs) for result in results)
        errors = [
            f"{result.source.name} / {name}: {message}"
            for result in results
            for name, message in result.errors.items()
        ]
        self.status_var.set(f"完成：生成 {output_count} 个文件。")
        if errors:
            messagebox.showwarning(
                "部分格式未完成",
                f"已生成 {output_count} 个文件。\n\n" + "\n".join(errors[:8]),
            )
        else:
            messagebox.showinfo("转换完成", f"已生成 {output_count} 个文件。\n{output_dir}")

    def _failed(self, message: str) -> None:
        self.progress.stop()
        self.start_button.configure(state="normal")
        self.status_var.set("转换未完成。")
        messagebox.showerror("转换失败", message)

    def _open_output(self) -> None:
        path = Path(self.output_var.get()).expanduser()
        path.mkdir(parents=True, exist_ok=True)
        os.startfile(path)  # type: ignore[attr-defined]


def main() -> None:
    root = tk.Tk()
    try:
        root.tk.call("tk", "scaling", 1.1)
    except tk.TclError:
        pass
    ConverterApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
