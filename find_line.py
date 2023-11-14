from tabula import read_pdf
import pandas as pd
import os
import pdfplumber


def find_line(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[219]
        # print(page.extract_text())
        print(len(page.chars))
        string = ""
        for char in page.chars:
            if char['size'] < 10:
                continue
            else:
                string += str(char['text'])
        
        print(string)

find_line("./FTA_pdfs/RCEP.pdf")

