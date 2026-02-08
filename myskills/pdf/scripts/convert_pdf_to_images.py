import os
import sys
import fitz  # pymupdf

def convert(pdf_path, output_dir, max_dim=1000):
    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        print(f"Error opening PDF: {e}")
        sys.exit(1)

    os.makedirs(output_dir, exist_ok=True)
    
    for i, page in enumerate(doc):
        # Calculate scaling to fit max_dim
        rect = page.rect
        width, height = rect.width, rect.height
        
        zoom = 1.0
        if width > max_dim or height > max_dim:
             zoom = min(max_dim / width, max_dim / height)
             
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat)
        
        image_path = os.path.join(output_dir, f"page_{i+1}.png")
        pix.save(image_path)
        print(f"Saved page {i+1} as {image_path} (size: {pix.width}x{pix.height})")
        
    print(f"Converted {len(doc)} pages to PNG images")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: convert_pdf_to_images.py [input pdf] [output directory] [max_dim (optional)]")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    output_directory = sys.argv[2]
    max_dim = int(sys.argv[3]) if len(sys.argv) > 3 else 1000
    
    convert(pdf_path, output_directory, max_dim)
