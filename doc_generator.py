import os
import re
import requests
from io import BytesIO
from bs4 import BeautifulSoup
from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, ListFlowable, ListItem
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from markdown import markdown
from reportlab.lib import colors

def convert_markdown_to_pdf(markdown_content, output_path, logo_url=None):
    # 1) Convert markdown → HTML fragment
    html_body = markdown(markdown_content, output_format='html5')
    
    # 2) Build full HTML fragment
    # session_html = f'<p><strong>Session ID:</strong> <code>{session_id}</code></p>'
    logo_html    = f'<img src="{logo_url}"/>' if logo_url else ''
    fragment     = logo_html + html_body

    # 3) **Wrap** in <body> so soup.body exists
    full_html = f"<html><body>{fragment}</body></html>"

    # 4) Parse with BeautifulSoup
    soup = BeautifulSoup(full_html, 'html.parser')

    # 5) Prepare ReportLab document (unchanged)…
    pdf_filename = f"medical_report_{session_id}.pdf"
    pdf_path     = os.path.join(output_path, pdf_filename)
    doc = SimpleDocTemplate(pdf_path, pagesize=letter,
                            rightMargin=72, leftMargin=72,
                            topMargin=72, bottomMargin=72)

    styles       = getSampleStyleSheet()
    normal       = styles['Normal']
    bullet_style = ParagraphStyle('Bullet', parent=normal,
                                  leftIndent=20, bulletIndent=10)
    story        = []

    # 6) Iterate over the wrapped <body> children
    for elem in soup.body.children:
        if getattr(elem, "name", None) == 'p':
            uls = elem.find_all('ul', recursive=False)
            if uls:
                for ul in uls:
                    items = [li.get_text(strip=True) for li in ul.find_all('li')]
                    lf = ListFlowable(
                        [ListItem(Paragraph(itm, normal), bulletColor=colors.black)
                         for itm in items],
                        bulletType='bullet'
                    )
                    story.append(lf)
                    story.append(Spacer(1, 0.1*inch))
            else:
                raw = str(elem)
                raw = re.sub(r'<br\s*/?>', '<br/>', raw)
                inner = re.sub(r'^<p>|</p>$', '', raw)
                story.append(Paragraph(inner, normal))
                story.append(Spacer(1, 0.1*inch))

        elif getattr(elem, "name", None) == 'img':
            src = elem.get('src')
            try:
                resp = requests.get(src)
                img_buf = BytesIO(resp.content)
                rl_img = Image(img_buf, width=2*inch, height=2*inch)
                story.append(rl_img)
                story.append(Spacer(1, 0.2*inch))
            except Exception:
                pass

    # 7) Build PDF
    doc.build(story)
    return pdf_path
