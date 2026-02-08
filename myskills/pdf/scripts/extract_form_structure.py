"""
Extract form structure from a non-fillable PDF using pymupdf.

This script analyzes the PDF to find:
- Text labels with their exact coordinates
- Horizontal lines (row boundaries)
- Checkboxes (small rectangles)

Output: A JSON file with the form structure.
Usage: python extract_form_structure.py <input.pdf> <output.json>
"""

import json
import sys
import fitz  # pymupdf

def extract_form_structure(pdf_path):
    structure = {
        "pages": [],
        "labels": [],
        "lines": [],
        "checkboxes": [],
        "row_boundaries": []
    }

    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        print(f"Error opening PDF: {e}")
        sys.exit(1)

    for page_num, page in enumerate(doc, 1):
        rect = page.rect
        structure["pages"].append({
            "page_number": page_num,
            "width": float(rect.width),
            "height": float(rect.height)
        })

        # text words
        words = page.get_text("words")
        # words format: (x0, y0, x1, y1, "word", block_no, line_no, word_no)
        for w in words:
            structure["labels"].append({
                "page": page_num,
                "text": w[4],
                "x0": round(float(w[0]), 1),
                "top": round(float(w[1]), 1),
                "x1": round(float(w[2]), 1),
                "bottom": round(float(w[3]), 1)
            })

        # vector drawings (lines, rects)
        drawings = page.get_drawings()
        for shape in drawings:
            # Lines
            if shape['items']:
                for item in shape['items']:
                    if item[0] == 'l': # line
                        p1, p2 = item[1], item[2]
                        # Horizontal line check: y roughly equal
                        if abs(p1.y - p2.y) < 2:
                            # Width check: significant portion of page relative to expectation
                            line_width = abs(p1.x - p2.x)
                            if line_width > rect.width * 0.5:
                                structure["lines"].append({
                                    "page": page_num,
                                    "y": round(float(p1.y), 1),
                                    "x0": round(float(min(p1.x, p2.x)), 1),
                                    "x1": round(float(max(p1.x, p2.x)), 1)
                                })
                    elif item[0] == 're': # rect
                        r = item[1] # fitz.Rect
                        width = r.width
                        height = r.height
                        # Checkbox heuristic (small square)
                        if 5 <= width <= 15 and 5 <= height <= 15 and abs(width - height) < 2:
                             structure["checkboxes"].append({
                                "page": page_num,
                                "x0": round(float(r.x0), 1),
                                "top": round(float(r.y0), 1),
                                "x1": round(float(r.x1), 1),
                                "bottom": round(float(r.y1), 1),
                                "center_x": round(float(r.x0 + r.x1) / 2, 1),
                                "center_y": round(float(r.y0 + r.y1) / 2, 1)
                            })

    # Deduce row boundaries
    lines_by_page = {}
    for line in structure["lines"]:
        page = line["page"]
        if page not in lines_by_page:
            lines_by_page[page] = []
        lines_by_page[page].append(line["y"])

    for page, y_coords in lines_by_page.items():
        y_coords = sorted(set(y_coords))
        for i in range(len(y_coords) - 1):
             # Ensure reasonably sized rows
            height = y_coords[i + 1] - y_coords[i]
            if height > 5:
                structure["row_boundaries"].append({
                    "page": page,
                    "row_top": y_coords[i],
                    "row_bottom": y_coords[i + 1],
                    "row_height": round(height, 1)
                })

    return structure

def main():
    if len(sys.argv) != 3:
        print("Usage: extract_form_structure.py [input.pdf] [output.json]")
        sys.exit(1)

    pdf_path = sys.argv[1]
    output_path = sys.argv[2]
    
    print(f"Extracting structure from {pdf_path}...")
    structure = extract_form_structure(pdf_path)

    with open(output_path, "w") as f:
        json.dump(structure, f, indent=2)

    print(f"Found:")
    print(f"  - {len(structure['pages'])} pages")
    print(f"  - {len(structure['labels'])} text labels")
    print(f"  - {len(structure['lines'])} horizontal lines")
    print(f"  - {len(structure['checkboxes'])} checkboxes")
    print(f"  - {len(structure['row_boundaries'])} row boundaries")
    print(f"Saved to {output_path}")

if __name__ == "__main__":
    main()
