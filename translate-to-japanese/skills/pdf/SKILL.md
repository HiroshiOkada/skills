---
name: pdf
description: ユーザーがPDFファイルで何かをしたい場合はいつでもこのスキルを使用してください。これには、PDFからのテキスト/テーブルの読み取りまたは抽出、複数のPDFの結合またはマージ、PDFの分割、ページの回転、透かしの追加、新しいPDFの作成、PDFフォームの記入、PDFの暗号化/復号化、画像の抽出、およびスキャンされたPDFを検索可能にするためのOCRが含まれます。ユーザーが.pdfファイルに言及したり、それを作成するように求めた場合、このスキルを使用してください。
license: Proprietary. LICENSE.txt has complete terms
---

# PDF処理ガイド

## 概要

このガイドは、Pythonライブラリとコマンドラインツールを使用した基本的なPDF処理操作をカバーしています。高度な機能、JavaScriptライブラリ、および詳細な例については、REFERENCE.mdを参照してください。PDFフォームに記入する必要がある場合は、FORMS.mdを読んでその指示に従ってください。

## クイックスタート

```python
from pypdf import PdfReader, PdfWriter

# PDFを読む
reader = PdfReader("document.pdf")
print(f"Pages: {len(reader.pages)}")

# テキストを抽出
text = ""
for page in reader.pages:
    text += page.extract_text()
```

## Pythonライブラリ

### pypdf - 基本操作

#### PDFのマージ
```python
from pypdf import PdfWriter, PdfReader

writer = PdfWriter()
for pdf_file in ["doc1.pdf", "doc2.pdf", "doc3.pdf"]:
    reader = PdfReader(pdf_file)
    for page in reader.pages:
        writer.add_page(page)

with open("merged.pdf", "wb") as output:
    writer.write(output)
```

#### PDFの分割
```python
reader = PdfReader("input.pdf")
for i, page in enumerate(reader.pages):
    writer = PdfWriter()
    writer.add_page(page)
    with open(f"page_{i+1}.pdf", "wb") as output:
        writer.write(output)
```

#### メタデータの抽出
```python
reader = PdfReader("document.pdf")
meta = reader.metadata
print(f"Title: {meta.title}")
print(f"Author: {meta.author}")
print(f"Subject: {meta.subject}")
print(f"Creator: {meta.creator}")
```

#### ページの回転
```python
reader = PdfReader("input.pdf")
writer = PdfWriter()

page = reader.pages[0]
page.rotate(90)  # 時計回りに90度回転
writer.add_page(page)

with open("rotated.pdf", "wb") as output:
    writer.write(output)
```

### pdfplumber - テキストとテーブルの抽出

#### レイアウト付きテキスト抽出
```python
import pdfplumber

with pdfplumber.open("document.pdf") as pdf:
    for page in pdf.pages:
        text = page.extract_text()
        print(text)
```

#### テーブル抽出
```python
with pdfplumber.open("document.pdf") as pdf:
    for i, page in enumerate(pdf.pages):
        tables = page.extract_tables()
        for j, table in enumerate(tables):
            print(f"Table {j+1} on page {i+1}:")
            for row in table:
                print(row)
```

#### 高度なテーブル抽出
```python
import pandas as pd

with pdfplumber.open("document.pdf") as pdf:
    all_tables = []
    for page in pdf.pages:
        tables = page.extract_tables()
        for table in tables:
            if table:  # テーブルが空でないか確認
                df = pd.DataFrame(table[1:], columns=table[0])
                all_tables.append(df)

# すべてのテーブルを結合
if all_tables:
    combined_df = pd.concat(all_tables, ignore_index=True)
    combined_df.to_excel("extracted_tables.xlsx", index=False)
```

### reportlab - PDF作成

#### 基本的なPDF作成
```python
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

c = canvas.Canvas("hello.pdf", pagesize=letter)
width, height = letter

# テキストを追加
c.drawString(100, height - 100, "Hello World!")
c.drawString(100, height - 120, "This is a PDF created with reportlab")

# 線を追加
c.line(100, height - 140, 400, height - 140)

# 保存
c.save()
```

#### 複数ページのPDF作成
```python
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet

doc = SimpleDocTemplate("report.pdf", pagesize=letter)
styles = getSampleStyleSheet()
story = []

# コンテンツを追加
title = Paragraph("Report Title", styles['Title'])
story.append(title)
story.append(Spacer(1, 12))

body = Paragraph("This is the body of the report. " * 20, styles['Normal'])
story.append(body)
story.append(PageBreak())

# 2ページ目
story.append(Paragraph("Page 2", styles['Heading1']))
story.append(Paragraph("Content for page 2", styles['Normal']))

# PDFをビルド
doc.build(story)
```

#### 下付き文字と上付き文字

**重要**: ReportLab PDFではUnicodeの下付き/上付き文字（₀₁₂₃₄₅₆₇₈₉, ⁰¹²³⁴⁵⁶⁷⁸⁹）を決して使用しないでください。組み込みフォントにはこれらのグリフが含まれていないため、黒いボックスとしてレンダリングされます。

代わりに、ParagraphオブジェクトでReportLabのXMLマークアップタグを使用してください：
```python
from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet

styles = getSampleStyleSheet()

# 下付き文字: <sub> タグを使用
chemical = Paragraph("H<sub>2</sub>O", styles['Normal'])

# 上付き文字: <super> タグを使用
squared = Paragraph("x<super>2</super> + y<super>2</super>", styles['Normal'])
```

キャンバス描画テキスト（Paragraphオブジェクトではない）の場合、Unicodeの下付き/上付き文字を使用するのではなく、フォントサイズと位置を手動で調整してください。

## コマンドラインツール

### pdftotext (poppler-utils)
```bash
# テキスト抽出
pdftotext input.pdf output.txt

# レイアウトを保持してテキスト抽出
pdftotext -layout input.pdf output.txt

# 特定のページを抽出
pdftotext -f 1 -l 5 input.pdf output.txt  # 1-5ページ
```

### qpdf
```bash
# PDFをマージ
qpdf --empty --pages file1.pdf file2.pdf -- merged.pdf

# ページ分割
qpdf input.pdf --pages . 1-5 -- pages1-5.pdf
qpdf input.pdf --pages . 6-10 -- pages6-10.pdf

# ページ回転
qpdf input.pdf output.pdf --rotate=+90:1  # 1ページ目を90度回転

# パスワード削除
qpdf --password=mypassword --decrypt encrypted.pdf decrypted.pdf
```

### pdftk (利用可能な場合)
```bash
# マージ
pdftk file1.pdf file2.pdf cat output merged.pdf

# 分割
pdftk input.pdf burst

# 回転
pdftk input.pdf rotate 1east output rotated.pdf
```

## 一般的なタスク

### スキャンされたPDFからテキストを抽出
```python
# 必要: pip install pytesseract pdf2image
import pytesseract
from pdf2image import convert_from_path

# PDFを画像に変換
images = convert_from_path('scanned.pdf')

# 各ページをOCR
text = ""
for i, image in enumerate(images):
    text += f"Page {i+1}:\n"
    text += pytesseract.image_to_string(image)
    text += "\n\n"

print(text)
```

### 透かしを追加
```python
from pypdf import PdfReader, PdfWriter

# 透かしを作成（または既存のものを読み込む）
watermark = PdfReader("watermark.pdf").pages[0]

# すべてのページに適用
reader = PdfReader("document.pdf")
writer = PdfWriter()

for page in reader.pages:
    page.merge_page(watermark)
    writer.add_page(page)

with open("watermarked.pdf", "wb") as output:
    writer.write(output)
```

### 画像の抽出
```bash
# pdfimages (poppler-utils) を使用
pdfimages -j input.pdf output_prefix

# これはすべての画像を output_prefix-000.jpg, output_prefix-001.jpg などのように抽出します
```

### パスワード保護
```python
from pypdf import PdfReader, PdfWriter

reader = PdfReader("input.pdf")
writer = PdfWriter()

for page in reader.pages:
    writer.add_page(page)

# パスワードを追加
writer.encrypt("userpassword", "ownerpassword")

with open("encrypted.pdf", "wb") as output:
    writer.write(output)
```

## クイックリファレンス

| タスク | 最適なツール | コマンド/コード |
|------|-----------|--------------|
| PDFのマージ | pypdf | `writer.add_page(page)` |
| PDFの分割 | pypdf | ファイルごとに1ページ |
| テキスト抽出 | pdfplumber | `page.extract_text()` |
| テーブル抽出 | pdfplumber | `page.extract_tables()` |
| PDF作成 | reportlab | Canvas または Platypus |
| コマンドラインマージ | qpdf | `qpdf --empty --pages ...` |
| OCRスキャンPDF | pytesseract | 最初に画像に変換 |
| PDFフォーム記入 | pdf-lib または pypdf (FORMS.md参照) | FORMS.md参照 |

## 次のステップ

- 高度なpypdfium2の使用法については、REFERENCE.mdを参照してください
- JavaScriptライブラリ（pdf-lib）については、REFERENCE.mdを参照してください
- PDFフォームに記入する必要がある場合は、FORMS.mdの指示に従ってください
- トラブルシューティングガイドについては、REFERENCE.mdを参照してください
