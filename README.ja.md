# PDF 原版忠実変換ツール

[简体中文](README.md) | [English](README.en.md) | [日本語](README.ja.md)

PDFを固定レイアウトEPUB、DOCX、旧形式のバイナリDOC、および必要に応じてTXTへ一括変換する、Windows向けローカルアプリケーションです。

## 最も重要なポイント

既定のモードは**原版忠実・固定レイアウト（推奨）**です。PDFの各ページをそのまま完全にレンダリングし、ページ全体の画像としてDOCX、DOC、またはEPUBへ格納します。そのため、出力形式によるページ順、文字位置、表、画像、注釈の外観、縦横方向、ページ比率の再配置を防げます。元のPDFは常に読み取り専用で扱います。

これは異なる形式間で元の見た目と構造を保持する最も確実な方法ですが、次の制限があります。

- 忠実変換された本文はページ画像の一部となるため、通常のWord文書のように文字単位では編集できません。
- 固定レイアウトEPUBは1ページずつ表示され、拡大縮小に対応します。小さい画面で細かい文字を読む場合はピンチ操作による拡大が必要です。文字をリフロー可能にすると、元の位置を同時に完全保持することはできません。

コピー、編集、OCRが必要な場合には編集可能テキストモードも利用できます。ただし、対象形式に合わせて再レイアウトされるため、原版と完全に同じ配置は保証できません。

## Windowsへのインストール

`PDF-Fidelity-Converter-Setup-0.3.0.exe` を実行し、スタートメニューから「PDF 原版保真转换器」を起動します。インストーラーには実行環境が含まれているため、Pythonを別途インストールする必要はありません。

- EPUBとDOCXの生成に追加ソフトウェアは不要です。
- 本物の旧形式 `.doc` を生成するには、デスクトップ版の[Microsoft Word](https://www.microsoft.com/microsoft-365/word)が必要です。本アプリはWordを検出し、Microsoft公式のWord Automationインターフェイスを使用します。
- スキャンPDFをTXT、編集可能テキスト、またはOCRモードで変換する場合に限り、Tesseract OCRと対象言語データ（`chi_sim`、`jpn`、`eng`など）が必要です。[Tesseractのインストールガイド](https://tesseract-ocr.github.io/tessdoc/Installation.html)を参照してください。

既定ではEPUBとDOCXが選択されます。Microsoft Wordが検出された場合はDOCも選択されます。TXTは既定では選択されません。

## 使用方法

1. 1つ以上のPDFを追加するか、フォルダーを追加してサブフォルダーを検索するか選択します。
2. **原版忠実・固定レイアウト（推奨）**を選択したままにします。
3. EPUB、DOCX、またはデスクトップ版Microsoft Wordがある場合はDOCを選択します。
4. 出力フォルダーを指定して変換を開始します。

元PDFごとに同名の結果フォルダーが作成されます。同名フォルダーが存在する場合は安全な別名が自動生成され、元ファイルは上書きされません。

## 2つの出力モード

### 原版忠実・固定レイアウト（既定）

- **DOCX:** PDFの各ページを、元ページと同じ向き・比率のWordページとして作成し、ページ全体の画像を左上に固定します。
- **DOC:** 上記DOCXを生成した後、Microsoft Wordの `SaveAs2` と `wdFormatDocument`（`0`）を使用し、本物のWord 97–2003バイナリDOCとして保存します。RTFやHTMLの拡張子だけを変更する方式ではありません。
- **EPUB:** 固定レイアウトEPUB 3です。PDFの各ページに1つのXHTMLページを作成し、`pre-paginated` と単ページ表示のメタデータを使用するため、スマートフォンやタブレットでの拡大閲覧に適しています。
- 印刷可能な注釈とフォームの外観もPDFページのレンダリングに含まれます。
- このモードでEPUB、DOCX、DOCだけを出力する場合、文字抽出やTesseractは不要です。

### 編集可能テキスト

- PDFに文字レイヤーがあれば優先して読み取り、文字レイヤーがない場合はTesseract OCRを利用できます。
- ページ順と行順の保持を試みますが、対象形式に合わせて内容が再配置されます。
- OCRには誤認識が生じる可能性があります。複雑な表、段組み、数式、特殊フォントの元構造は保証できません。

## TXT

TXTはUTF-8で保存され、追加のページ見出しは挿入せず、ページ間を改ページ文字（`\f`）で区切ります。TXTは画像、フォント、表、固定ページ形状を保持できないため、視覚的に完全な形式ではありません。

## ローカル検証結果

バージョン0.3.0では、次の内容を含む複数ページPDFで検証しました。

- A4縦ページ：文字、表、埋め込み画像
- A4横ページ：グラフ、画像、回転文字
- 4 × 6インチのカスタムページ：全面スキャン画像

検証結果：

- DOCXは正常に再オープンでき、ページ順、向き、比率、画像、構造が一致し、余分な空白ページや切り抜きはありませんでした。
- EPUBはEPUBCheck 5.3.0でfatal 0、error 0、warning 0、info 0でした。
- 自動テストでは、元PDFのハッシュ不変、固定レイアウトメタデータ、DOCX画像の固定配置、EPUB/DOCX内のページ画像とPDF基準レンダリングの一致、Microsoft Word自動化スクリプト、マクロ無効化、DOCバイナリヘッダー、デスクトップ既定出力、外部依存がない場合の明確なエラーを確認しています。

ビルド環境にはMicrosoft Wordがインストールされていなかったため、実際のWord COMからDOCへの往復検証は完了していません。Wordがない場合、DOCだけが無効になり、EPUB、DOCX、TXTは利用できます。各Windows環境でDOC経路を完全検証済みと判断するには、実際のDOC検証が必要です。

閲覧アプリによって拡大率、ページの影、アンチエイリアス表示にわずかな差が生じることがありますが、ページ内容の再構成は行いません。

## 開発者向け

仮想環境へソースをインストールします。

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
```

既定の忠実変換を実行します。

```powershell
.\.venv\Scripts\pdf-full-convert.exe "D:\資料" -o "D:\変換結果" -f epub -f docx --style visual
```

Microsoft Wordで旧形式DOCを生成します。

```powershell
.\.venv\Scripts\pdf-full-convert.exe "D:\資料" -o "D:\変換結果" -f doc --style visual --word "C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE"
```

テストを実行します。

```powershell
python -m unittest discover -s tests -v
```

## オープンソースコンポーネント

- [pypdf](https://github.com/py-pdf/pypdf)：PDFの文字レイヤーを読み取ります。
- [pypdfium2](https://github.com/pypdfium2-team/pypdfium2)：PDFページを忠実にレンダリングします。
- [python-docx](https://github.com/python-openxml/python-docx)：DOCXを生成します。
- [Tesseract](https://github.com/tesseract-ocr/tesseract)：任意のOCR機能を提供します。
- [Microsoft Word Automation](https://learn.microsoft.com/en-us/office/vba/api/word.application)：ユーザーがインストール済みのデスクトップ版Wordを呼び出して旧形式DOCを生成します。Microsoft Word自体は本プロジェクトに同梱されません。
- [PyInstaller](https://github.com/pyinstaller/pyinstaller)と[Inno Setup](https://github.com/jrsoftware/issrc)：Windowsアプリとインストーラーを作成します。

第三者ライセンスの詳細は `THIRD-PARTY-NOTICES.md` を参照してください。

## ライセンス

本プロジェクトのソースコードはMIT Licenseで公開されています。第三者コンポーネントにはそれぞれのライセンスが適用されます。
