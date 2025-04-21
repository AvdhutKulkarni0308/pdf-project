from PyPDF2 import PdfReader, PdfWriter

def compress_pdf(input_path):
    reader = PdfReader(input_path)
    writer = PdfWriter()

    for page in reader.pages:
        # Add each page to the writer
        writer.add_page(page)
        
        # Apply compression to each page's contents
        page.compress_content_streams()

    # Preserve metadata
    writer.add_metadata(reader.metadata)

    return writer