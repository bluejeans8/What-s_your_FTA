import pdfplumber

pdf_path = "/home/jsk0821/Documents/FTA/FTA_pdfs/EU/EU_agreement_Algeria_20051010.pdf"

with pdfplumber.open(pdf_path) as pdf:
    with open("./example.txt", "w") as wf:
        for page in pdf.pages:
            wf.write(page.extract_text(x_tolerance=1)
)

