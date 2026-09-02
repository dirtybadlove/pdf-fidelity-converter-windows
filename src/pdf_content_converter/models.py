from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Callable


SUPPORTED_FORMATS = ("txt", "epub", "docx", "doc")


class OcrMode(str, Enum):
    AUTO = "auto"
    FULL = "full"
    NEVER = "never"


class OutputStyle(str, Enum):
    EDITABLE = "editable"
    VISUAL = "visual"


ProgressCallback = Callable[[str], None]


@dataclass(slots=True)
class ConversionOptions:
    output_dir: Path
    formats: tuple[str, ...] = SUPPORTED_FORMATS
    ocr_mode: OcrMode = OcrMode.AUTO
    ocr_language: str = "chi_sim+jpn+eng"
    output_style: OutputStyle = OutputStyle.VISUAL
    dpi: int = 240
    recursive: bool = True
    tesseract_cmd: str | None = None
    word_cmd: str | None = None

    def validate(self) -> None:
        invalid = sorted(set(self.formats) - set(SUPPORTED_FORMATS))
        if invalid:
            raise ValueError(f"不支持的输出格式: {', '.join(invalid)}")
        if not self.formats:
            raise ValueError("至少选择一种输出格式。")
        if not 96 <= self.dpi <= 600:
            raise ValueError("DPI 必须在 96 到 600 之间。")
        if not self.ocr_language.strip():
            raise ValueError("OCR 语言不能为空。")


@dataclass(slots=True)
class PageContent:
    number: int
    text: str
    width_pt: float
    height_pt: float
    image_path: Path | None = None
    used_ocr: bool = False


@dataclass(slots=True)
class ConversionResult:
    source: Path
    outputs: dict[str, Path] = field(default_factory=dict)
    errors: dict[str, str] = field(default_factory=dict)
    ocr_pages: list[int] = field(default_factory=list)

    @property
    def succeeded(self) -> bool:
        return bool(self.outputs) and not self.errors
