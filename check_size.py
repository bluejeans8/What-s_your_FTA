import pandas as pd
import os
import pdfplumber


pdf_path = "./FTA_pdfs/text_of_agreement_eng_한-뉴질랜드_FTA.pdf"

# footnote 글씨 크기 check 용도
def check_size(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[10]
        print(len(page.chars))
        string = ""
        for char in page.chars:
            if char['size'] < 10:
                continue
            else:
                string += str(char['text'])
        
        print(string)

check_size(pdf_path)

