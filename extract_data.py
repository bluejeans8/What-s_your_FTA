import pandas as pd
import os
import pdfplumber
import re


# PDF 정보
# width 595.44
# height 841.68


def extract_info(pdf_path):

    table, text = "", ""

    data = []

    with pdfplumber.open(pdf_path) as pdf:
        page_cnt = 0
        for page in pdf.pages:
            page_cnt += 1
            if page_cnt%100 == 0:
                print(page_cnt)
            
            # table이 포함된 boundary boxes 생성
            boxes = []
            t_locations = page.find_tables()
            for t_location in t_locations:
                bounding_box = t_location.bbox
                boxes.append(bounding_box)    


            page_width = 595.44
            page_height = 841.68
            prev_table_box = (0,0,595,0)
            pad_size = 1

            for box in boxes:
                # table 사이사이의 text 추출
                page_upward_table = page.within_bbox((0,prev_table_box[3],page_width-1,box[1]))
                # text = page_upward_table.extract_text()
                text = ""
                for char in page_upward_table.chars:
                    if char['size'] < 10:
                        continue
                    else:
                        text += str(char['text'])
                data.append(text)
                
                # table 추출
                padded_box = (box[0] - pad_size, box[1] - pad_size, box[2] + pad_size, box[3] + pad_size)
                page_in_table = page.within_bbox(padded_box)
                table = page_in_table.extract_table()
                data.append(str(table))

                prev_table_box = box
            
            # 제일 아래 table 밑의 text 추출
            page_below_final_table = page.within_bbox((0,prev_table_box[3],page_width-1,page_height-1))

            text = ""
            for char in page_below_final_table.chars:
                if char['size'] < 10:
                    continue
                else:
                    text += str(char['text'])
            data.append(text)


            # text = page_below_final_table.extract_text()
            
            # # page number 제거
            # text = re.sub(r"[0-9]+[A-Z]*-[0-9]+","",text)[:-1]
            # if text != "":
            #     data.append(text)

            
    path = f"./FTA_data/{pdf_path}"
    if not os.path.exists(path):
        os.makedirs(path)


    with open(f"./FTA_data/{pdf_path}/text.txt", "w", encoding='utf-8') as wf:
        for d in data:
            if d.strip():
                wf.write(str(d)+"\n")


extract_info("./FTA_pdfs/RCEP.pdf")
        






# def extract_table(pdf_path):
#     with pdfplumber.open(pdf_path) as pdf:
#         # Assuming there's only one page; you may loop through pages if needed
        
        
#         page = pdf.pages[57]
#         table = page.extract_table()

#     return table


# def get_text(pdf_path):
#     pdf=pdfplumber.open(pdf_path)
#     pages = pdf.pages
#     page = pages[57]
#     print(page.find_tables()[0].bbox)
#     # for page in pages:
#     #     print(page.extract_text())


# # Example usage
# pdf_path = './FTA_pdfs/RCEP.pdf'
# # table_data = extract_table(pdf_path)
# # print(table_data)

# get_text(pdf_path)


# # PDF 파일 경로
# name = "RCEP"
# pdf_path = f"./FTA_pdfs/{name}.pdf"  # 여기에 PDF 파일 경로를 입력하세요.
# # PDF 파일에서 표 추출
# # 'pages' 매개변수를 통해 특정 페이지만 선택할 수 있습니다. 'all'은 모든 페이지를 의미합니다.
# # 413-420
# tables = read_pdf(pdf_path, pages='57-212', multiple_tables=True, stream=True)
# # 추출된 표를 각각 CSV 파일로 저장
# for i, table in enumerate(tables):
#     # 생성할 CSV 파일명
#     path = f"./FTA_data/{name}"

#     if not os.path.exists(path):
#         os.makedirs(path)

#     csv_file = f"./FTA_data/{name}/extracted_table_{i}.csv"
#     # CSV 파일로 저장
#     table.to_csv(csv_file, index=False)
#     print(f"Table {i} saved as {csv_file}")