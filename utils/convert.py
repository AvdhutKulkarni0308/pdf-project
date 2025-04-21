import img2pdf
from PIL import Image
import os

def convert_image_to_pdf(image_path):
    # Convert image to PDF
    try:
        # First open the image to verify it and get its format
        image = Image.open(image_path)
        # Convert RGBA to RGB if necessary (PDF doesn't support RGBA)
        if image.mode == 'RGBA':
            image = image.convert('RGB')
        
        # Create temporary path for the converted image if needed
        temp_path = image_path
        if image.format not in ['JPEG', 'PNG']:
            temp_path = os.path.splitext(image_path)[0] + '.jpg'
            image.save(temp_path, 'JPEG')
        
        # Convert to PDF
        pdf_bytes = img2pdf.convert(temp_path)
        
        # If we created a temporary file, clean it up
        if temp_path != image_path:
            os.remove(temp_path)
            
        return pdf_bytes
        
    except Exception as e:
        raise Exception(f"Error converting image to PDF: {str(e)}")