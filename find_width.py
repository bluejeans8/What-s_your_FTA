import pandas as pd
import os
import pdfplumber


def find_width(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[414]
        print(page.width)
        print(page.height)


find_width("./FTA_pdfs/RCEP.pdf")