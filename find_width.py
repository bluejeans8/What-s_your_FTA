import pandas as pd
import os
import pdfplumber


def find_width(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[2040]
        print(page.extract_text())
        page_in_box = page.within_bbox((0,0, page.width, page.height - 80))
        print(page_in_box.extract_text())

        print(page.find_table().bbox)

find_width("/home/jsk0821/Documents/FTA/FTA_pdfs/한-중미 FTA.pdf")