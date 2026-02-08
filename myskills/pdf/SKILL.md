---
name: pdf
description: Use this skill whenever the user wants to do anything with PDF files. This includes reading or extracting text/tables from PDFs, combining or merging multiple PDFs into one, splitting PDFs apart, rotating pages, adding watermarks, creating new PDFs, filling PDF forms, encrypting/decrypting PDFs, extracting images, and OCR on scanned PDFs to make them searchable. If the user mentions a .pdf file or asks to produce one, use this skill.
license: Proprietary. LICENSE.txt has complete terms
---

# Configuration

**IMPORTANT**:
- **Python Path**: `C:\Users\okada\skill-env\.venv\Scripts\python.exe`
- **Libraries**:
    - `pdfminer-six >= 20260107`
    - `pymupdf >= 1.26.7` (fitz)
    - `pypdf >= 6.6.2`

When writing or modifying scripts for this skill, ensure they are compatible with these versions and utilize their features maximally.

# PDF Processing Guide

## Overview

This guide covers essential PDF processing operations using Python libraries and command-line tools. For advanced features, JavaScript libraries, and detailed examples, see REFERENCE.md. If you need to fill out a PDF form, read FORMS.md and follow its instructions.

## Quick Start

```python
import fitz  # pymupdf

# Read a PDF
doc = fitz.open("document.pdf")
print(f"Pages: {len(doc)}")

# Extract text
text = ""
for page in doc:
    text += page.get_text()
print(text)
```

## Python Libraries

### pymupdf (fitz) - The Powerhouse

PyMuPDF is a high-performance library for data extraction, analysis, conversion, and manipulation of PDFs. It is the recommended tool for most tasks.

#### Merge PDFs
```python
import fitz

doc_a = fitz.open("doc1.pdf")
doc_b = fitz.open("doc2.pdf")

doc_a.insert_pdf(doc_b)
doc_a.save("merged.pdf")
```

#### Split PDF
```python
doc = fitz.open("input.pdf")
# Save pages 0 and 1 to a new file
doc.select([0, 1]) 
doc.save("first_two_pages.pdf")
```

#### Extract Text
```python
doc = fitz.open("document.pdf")
for page in doc:
    # "text": plain text with line breaks
    # "blocks": list of text blocks with coordinates
    # "words": list of words with coordinates
    print(page.get_text("text"))
```

#### Extract Tables
PyMuPDF has a built-in table finder:
```python
doc = fitz.open("document.pdf")
page = doc[0]
tabs = page.find_tables()
if tabs.tables:
    print(tabs[0].extract())
```

#### Render Page to Image
```python
doc = fitz.open("document.pdf")
page = doc[0]
pix = page.get_pixmap(dpi=150)
pix.save("page_1.png")
```

#### Create/Modify PDF
You can insert text, shapes, and images:
```python
doc = fitz.open("input.pdf") # or fitz.open() to create new
page = doc[0] # or doc.new_page()

# Insert Text
page.insert_text((50, 72), "Hello World!", fontsize=12, color=(0, 0, 1))

# Draw Shape
shape = page.new_shape()
shape.draw_rect((50, 100, 200, 200))
shape.finish(color=(1, 0, 0), width=2)
shape.commit()

doc.save("modified.pdf")
```

### pypdf - Pure Python Operations

Reference `pypdf` for tasks like encryption, detailed metadata manipulation, or simple merges/splits if you prefer a pure Python approach.

#### Merge PDFs
```python
from pypdf import PdfWriter

merger = PdfWriter()
for pdf in ["file1.pdf", "file2.pdf"]:
    merger.append(pdf)
merger.write("merged-pypdf.pdf")
```

#### Split PDF
```python
from pypdf import PdfReader, PdfWriter

reader = PdfReader("input.pdf")
for i, page in enumerate(reader.pages):
    writer = PdfWriter()
    writer.add_page(page)
    with open(f"page_{i}.pdf", "wb") as f:
        writer.write(f)
```

#### Password Protection
```python
from pypdf import PdfReader, PdfWriter

reader = PdfReader("input.pdf")
writer = PdfWriter()
writer.append_pages_from_reader(reader)
writer.encrypt("user_password", "owner_password")

with open("encrypted.pdf", "wb") as f:
    writer.write(f)
```

## Common Tasks

### Extract Images
Using `pymupdf`:
```python
import fitz

doc = fitz.open("input.pdf")
for i, page in enumerate(doc):
    for img in page.get_images():
        xref = img[0]
        pix = fitz.Pixmap(doc, xref)
        if pix.n - pix.alpha > 3: # CMYK: convert to RGB first
            pix = fitz.Pixmap(fitz.csRGB, pix)
        pix.save(f"p{i}_img{xref}.png")
```

### Add Watermark
Using `pypdf`:
```python
from pypdf import PdfReader, PdfWriter

reader = PdfReader("source.pdf")
watermark = PdfReader("watermark.pdf").pages[0]
writer = PdfWriter()

for page in reader.pages:
    page.merge_page(watermark)
    writer.add_page(page)

with open("watermarked.pdf", "wb") as f:
    writer.write(f)
```

## Quick Reference

| Task | Recommended Tool | Method |
|------|-----------|--------------|
| Text Extraction | pymupdf | `page.get_text()` |
| Table Extraction | pymupdf | `page.find_tables()` |
| Image Extraction | pymupdf | `page.get_images()` |
| Render to Image | pymupdf | `page.get_pixmap()` |
| Merge/Split | pymupdf / pypdf | `insert_pdf` / `PdfWriter` |
| Create PDF | pymupdf | `doc.new_page()`, `page.insert_text()` |
| Forms (Fill) | pypdf | `writer.update_page_form_field_values()` |
| Encryption | pypdf | `writer.encrypt()` |

## Next Steps

- For filling forms, pypdf is robust. `pymupdf` also supports widgets but pypdf is often easier for simple filling.
- For detailed content layout analysis, `pdfminer.six` is available if `pymupdf` results need verification.
