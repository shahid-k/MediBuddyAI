from md2pdf.core import md2pdf

def save_markdown_pdf(filename, markdown_content, css_path='./report_style.css'):
    # Optionally provide a .css file for custom styling, else uses default
    md2pdf(filename, md_content=markdown_content, css_file=css_path)
    return filename
