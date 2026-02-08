import sys
import json
import fitz  # pymupdf

def create_validation_image(page_number, fields_json_path, input_path, output_path):
    # input_path can be pdf or image.
    try:
        doc = fitz.open(input_path)
    except Exception as e:
        print(f"Error opening input: {e}")
        sys.exit(1)
        
    # If it's a PDF, select the page. If it's an image, it has 1 page (index 0).
    if doc.is_pdf:
        if page_number < 1 or page_number > len(doc):
             print(f"Error: Page number {page_number} out of range (1-{len(doc)})")
             sys.exit(1)
        page = doc[page_number - 1]
    else:
        # Assuming input is an image that corresponds to the page
        page = doc[0]

    with open(fields_json_path, 'r') as f:
        data = json.load(f)
        
    num_boxes = 0
    
    # Draw red for entry, blue for label
    shape = page.new_shape()
    
    for field in data["form_fields"]:
         # Only draw if the field belongs to this page
         # Note: JSON usually uses 1-based indexing for pages
        if field["page_number"] == page_number:
            entry_box = field['entry_bounding_box'] # [x0, y0, x1, y1]
            label_box = field['label_bounding_box']
            
            # fitz.Rect takes (x0, y0, x1, y1)
            shape.draw_rect(fitz.Rect(entry_box))
            shape.finish(color=(1, 0, 0), width=2) # Red
            
            shape.draw_rect(fitz.Rect(label_box))
            shape.finish(color=(0, 0, 1), width=2) # Blue
            
            num_boxes += 2
            
    shape.commit()
    
    # Render to image
    # Use higher dpi for better visibility
    pix = page.get_pixmap(dpi=150) 
    pix.save(output_path)
    print(f"Created validation image at {output_path} with {num_boxes} bounding boxes")


if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: create_validation_image.py [page number] [fields.json file] [input file path] [output image path]")
        sys.exit(1)
    page_number = int(sys.argv[1])
    fields_json_path = sys.argv[2]
    input_file_path = sys.argv[3]
    output_image_path = sys.argv[4]
    create_validation_image(page_number, fields_json_path, input_file_path, output_image_path)
