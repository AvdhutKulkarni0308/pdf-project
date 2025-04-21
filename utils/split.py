from PyPDF2 import PdfReader, PdfWriter

def split_pdf(input_path, page_number):
    reader = PdfReader(input_path)
    total_pages = len(reader.pages)
    
    if page_number < 1 or page_number > total_pages:
        raise ValueError(f"Invalid page number. Please enter a number between 1 and {total_pages}")
    
    # Create first part
    writer1 = PdfWriter()
    for page in range(page_number - 1):
        writer1.add_page(reader.pages[page])
    
    # Create second part
    writer2 = PdfWriter()
    for page in range(page_number - 1, total_pages):
        writer2.add_page(reader.pages[page])
    
    # Save both parts
    output_path1 = 'part1.pdf'
    output_path2 = 'part2.pdf'
    
    with open(f'results/{output_path1}', 'wb') as output1:
        writer1.write(output1)
    with open(f'results/{output_path2}', 'wb') as output2:
        writer2.write(output2)
    
    return [output_path1, output_path2]