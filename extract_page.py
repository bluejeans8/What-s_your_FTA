import pdfplumber

pdf_path = ".\\FTA_pdfs\\EU\\EU_agreement_Andorra_2003_1.pdf"

with pdfplumber.open(pdf_path) as pdf:
    for page in pdf.pages:
        print(page.extract_text())