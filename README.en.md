# PDF Fidelity Converter

[简体中文](README.md) | [English](README.en.md) | [日本語](README.ja.md)

A local Windows application for batch-converting PDFs to fixed-layout EPUB, DOCX, legacy binary DOC, and optionally TXT.

## The most important point

The default mode is **Fidelity-first fixed layout (recommended)**. Every PDF page is rendered in full and inserted as a full-page image into DOCX, DOC, or EPUB. This prevents the output format from reflowing page order, text positions, tables, images, annotation appearance, orientation, or page proportions. The source PDF is always opened read-only.

This is the most reliable way to preserve the original visual structure across formats, with two honest limitations:

- Text in fidelity output is part of a page image and cannot be edited word by word like ordinary Word text.
- Fixed-layout EPUB displays one page at a time and supports zooming. Fine text may require pinch-to-zoom on small screens. Reflowable text cannot preserve every original position at the same time.

An editable-text mode remains available for copying, editing, or OCR workflows, but it reflows content and therefore cannot guarantee an unchanged layout.

## Windows installation

Run `PDF-Fidelity-Converter-Setup-0.3.0.exe`, then launch **PDF Fidelity Converter** from the Start menu. The installer includes the application runtime, so Python is not required separately.

- EPUB and DOCX require no additional software.
- A genuine legacy `.doc` file requires the desktop edition of [Microsoft Word](https://www.microsoft.com/microsoft-365/word). The application locates Word and uses Microsoft's Word Automation interface.
- Tesseract OCR and the relevant language data, such as `chi_sim`, `jpn`, or `eng`, are needed only when a scanned PDF is converted through TXT, editable-text, or OCR mode. See the [Tesseract installation guide](https://tesseract-ocr.github.io/tessdoc/Installation.html).

EPUB and DOCX are selected by default. DOC is also selected when Microsoft Word is detected. TXT is not selected by default.

## How to use

1. Add one or more PDFs, or add a folder and choose whether to scan its subfolders.
2. Keep **Fidelity-first fixed layout (recommended)** selected.
3. Select EPUB, DOCX, or DOC when desktop Microsoft Word is available.
4. Choose an output directory and start the conversion.

Each source PDF receives a same-named result folder. Name conflicts are resolved with a safe unique directory, and source files are never overwritten.

## Output modes

### Fidelity-first fixed layout (default)

- **DOCX:** each PDF page becomes one Word page with the same orientation and proportions; the full-page image is anchored at the upper-left corner.
- **DOC:** the application first creates the fidelity DOCX, then uses Microsoft Word's `SaveAs2` method with `wdFormatDocument` (`0`) to create a genuine Word 97–2003 binary document. It does not disguise RTF or HTML by changing the extension.
- **EPUB:** fixed-layout EPUB 3, with one XHTML document per PDF page and `pre-paginated` single-page metadata for phone and tablet viewing.
- Printable annotations and the visual appearance of form fields are included in page rendering.
- Tesseract and text extraction are not required when this mode outputs only EPUB, DOCX, or DOC.

### Editable text

- The application first reads an existing PDF text layer and can use Tesseract OCR when none is available.
- It attempts to preserve page and line order, but the target format reflows the content.
- OCR may contain recognition errors. Complex tables, multiple columns, formulas, and special fonts cannot be guaranteed to retain their original structure.

## TXT

TXT output uses UTF-8, adds no artificial page headings, and separates pages with a form-feed character (`\f`). TXT cannot contain images, fonts, tables, or fixed page geometry, so it is not a visually lossless format.

## Local validation

Version 0.3.0 was tested with a multi-page PDF containing:

- an A4 portrait page with text, a table, and an embedded image;
- an A4 landscape page with a chart, images, and rotated text;
- a 4 × 6 inch custom page containing a full-page scanned image.

Verified results:

- DOCX reopened successfully with the correct page order, orientation, proportions, images, and structure, without extra blank pages or cropping.
- EPUB passed EPUBCheck 5.3.0 with 0 fatal errors, 0 errors, 0 warnings, and 0 info messages.
- Automated tests cover unchanged source-PDF hashes, fixed-layout metadata, anchored DOCX images, embedded EPUB/DOCX page images matching the PDF reference render, Microsoft Word automation scripts, disabled macros, binary DOC header checks, desktop-default output, and clear errors for missing external dependencies.

Microsoft Word was not installed on the build machine, so an actual Word COM-to-DOC round-trip could not be completed there. Without Word, the application disables only DOC and continues to support EPUB, DOCX, and TXT. A real DOC validation is still required on each Windows environment before its DOC path can be considered fully verified.

Readers may differ slightly in zoom, page shadows, or anti-aliasing, but the application does not reorganize page content.

## Development

Install the source in a virtual environment:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
```

Run a default fidelity conversion:

```powershell
.\.venv\Scripts\pdf-full-convert.exe "D:\Documents" -o "D:\Converted" -f epub -f docx --style visual
```

Generate legacy DOC through Microsoft Word:

```powershell
.\.venv\Scripts\pdf-full-convert.exe "D:\Documents" -o "D:\Converted" -f doc --style visual --word "C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE"
```

Run the tests:

```powershell
python -m unittest discover -s tests -v
```

## Open-source components

- [pypdf](https://github.com/py-pdf/pypdf) reads PDF text layers.
- [pypdfium2](https://github.com/pypdfium2-team/pypdfium2) renders PDF pages faithfully.
- [python-docx](https://github.com/python-openxml/python-docx) creates DOCX files.
- [Tesseract](https://github.com/tesseract-ocr/tesseract) provides optional OCR.
- [Microsoft Word Automation](https://learn.microsoft.com/en-us/office/vba/api/word.application) calls the user's installed desktop Word to create legacy DOC files. Microsoft Word is not distributed with this project.
- [PyInstaller](https://github.com/pyinstaller/pyinstaller) and [Inno Setup](https://github.com/jrsoftware/issrc) build the Windows application and installer.

See `THIRD-PARTY-NOTICES.md` for complete third-party notices.

## License

Project source code is released under the MIT License. Third-party components remain subject to their respective licenses.
