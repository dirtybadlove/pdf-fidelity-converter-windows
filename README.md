# PDF 原版保真转换器

[简体中文](README.md) | [English](README.en.md) | [日本語](README.ja.md)

一个本地运行的 Windows PDF 批量转换工具，可输出固定版式 EPUB、DOCX、旧版二进制 DOC，也可选输出 TXT。

## 最重要的结论

软件默认使用“原版保真固定版式（推荐）”：每个 PDF 页面先完整渲染，再作为一张整页图像写入 DOCX、DOC 或 EPUB。因此页面顺序、文字位置、表格、图片、批注外观、横竖方向和页面比例不会被重新排版，源 PDF 也始终只读。

这是“不改变原文结构和图片”与跨格式兼容之间最可靠的方案，但有两个诚实的限制：

- 保真输出中的正文是整页图像，不能像普通 Word 文档那样逐字编辑。
- 固定版式 EPUB 会在手机上“一页一屏”显示并支持缩放；小屏阅读细字时可能需要双指放大。若改为自动重排文字，就无法同时保持原 PDF 的位置和结构。

可编辑文字模式仍然保留给需要复制、修改或 OCR 的场景，但它会按目标格式重新排版，不能承诺版式完全不变。

## Windows 安装

普通用户只需运行：

`PDF-Fidelity-Converter-Setup-0.3.0.exe`

安装后从开始菜单打开“PDF 原版保真转换器”。安装包自带运行环境，不要求另外安装 Python。

- 生成 EPUB、DOCX：无需额外软件。
- 生成真正的旧版 `.doc`：需要安装桌面版 [Microsoft Word](https://www.microsoft.com/microsoft-365/word)，软件会自动寻找并通过微软的 Word Automation 接口调用它。
- 只有使用 TXT、可编辑文字或 OCR 时，扫描 PDF 才需要安装 [Tesseract OCR](https://tesseract-ocr.github.io/tessdoc/Installation.html) 及对应语言数据，例如 `chi_sim`、`jpn`、`eng`。

默认勾选 EPUB 和 DOCX。检测到 Microsoft Word 时会同时勾选 DOC；TXT 默认不勾选。

## 使用方法

1. 添加一个或多个 PDF，或者添加文件夹并选择是否扫描子文件夹。
2. 保持“原版保真固定版式（推荐）”。
3. 勾选 EPUB、DOCX，或在已安装桌面版 Microsoft Word 时勾选 DOC。
4. 选择输出目录并开始转换。

每个源 PDF 会得到一个同名结果文件夹。重名时软件会自动生成安全的独立目录，不覆盖源文件。

## 两种输出模式

### 原版保真固定版式（默认）

- DOCX：每个 PDF 页面对应一个 Word 页面，使用与原页一致的方向和比例，整页图像锚定在页面左上角。
- DOC：先生成上述 DOCX，再通过 Microsoft Word 的 `SaveAs2` 接口以 `wdFormatDocument`（值 0）保存为真正的 Word 97–2003 二进制 DOC，不用 RTF、HTML 或改扩展名冒充。
- EPUB：固定版式 EPUB 3；每个 PDF 页面对应一个 XHTML 页面，使用 `pre-paginated` 和单页显示元数据，适合手机、平板缩放阅读。
- 表单外观和可打印批注会参与 PDF 页面渲染。
- 此模式只输出 EPUB/DOCX/DOC 时不需要文字提取，也不需要 Tesseract。

### 可编辑文字

- 优先读取 PDF 自带文字层；没有文字层时可使用 Tesseract OCR。
- 尽量保留页次与行序，但目标格式会重新排版。
- OCR 可能识别错字，复杂表格、多栏、公式和特殊字体不能保证原结构。

## TXT

TXT 使用 UTF-8 编码，不添加额外页标题，页面之间以换页符 `\f` 分隔。TXT 本身不支持图片、字体、表格和固定页面布局，因此不属于“视觉结构不变”的输出格式。

## 本地验证结果

版本 0.3.0 继续使用一份包含以下内容的多页 PDF 验证保真输出：

- A4 纵向页：文字、表格和嵌入图片；
- A4 横向页：图表、图片和旋转文字；
- 4×6 英寸自定义页面：整页扫描图像。

验证结果：

- DOCX 可以重新打开，页序、方向、比例、图片与结构一致，无额外空白页或裁切。
- EPUB 通过官方 EPUBCheck 5.3.0：0 fatal、0 error、0 warning、0 info。
- 自动化测试覆盖源 PDF 哈希不变、固定版式元数据、DOCX 锚定图片、EPUB/DOCX 内嵌页图与 PDF 基准渲染一致、Microsoft Word 自动化脚本、宏禁用设置、DOC 二进制文件头校验，以及缺少外部依赖时的明确错误。

当前构建机没有安装 Microsoft Word，因此本机不能完成真实 Word COM → DOC 的端到端回读。程序会在未检测到 Word 时只阻止 DOC，不影响 EPUB、DOCX 和 TXT；在安装了桌面版 Word 的 Windows 电脑上仍需完成一次真实 DOC 验收后，才能声称该环境的 DOC 链路已完全验证。

不同阅读器可能在缩放、页边阴影或抗锯齿上略有显示差异，但不会重新组织页面内容。

## 开发者使用

安装源码：

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
```

默认保真转换：

```powershell
.\.venv\Scripts\pdf-full-convert.exe "D:\资料" -o "D:\转换结果" -f epub -f docx --style visual
```

需要旧版 DOC：

```powershell
.\.venv\Scripts\pdf-full-convert.exe "D:\资料" -o "D:\转换结果" -f doc --style visual --word "C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE"
```

运行测试：

```powershell
python -m unittest discover -s tests -v
```

## GitHub 开源组件

- [pypdf](https://github.com/py-pdf/pypdf)：读取 PDF 文字层。
- [pypdfium2](https://github.com/pypdfium2-team/pypdfium2)：将 PDF 页面按原样渲染。
- [python-docx](https://github.com/python-openxml/python-docx)：生成 DOCX。
- [Tesseract](https://github.com/tesseract-ocr/tesseract)：可选的扫描文字识别。
- [Microsoft Word Automation](https://learn.microsoft.com/en-us/office/vba/api/word.application)：调用用户已经安装的桌面版 Word 生成旧版 DOC；Word 本身不随本软件分发。
- [PyInstaller](https://github.com/pyinstaller/pyinstaller) 与 [Inno Setup](https://github.com/jrsoftware/issrc)：生成 Windows 应用和安装程序。

完整第三方许可提示见 `THIRD-PARTY-NOTICES.md`。

## 许可证

本项目代码使用 MIT License。第三方组件分别遵循其自己的许可证。
