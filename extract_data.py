import pandas as pd
import os
import pdfplumber
import re


# PDF 정보
# width 595.44
# height 841.68

pdf_path = "./FTA_pdfs/RCEP.pdf"


## 테이블 병합 알고리즘:
## 두 테이블 사이에 텍스트가 껴 있는 경우 다른 테이블, 없는 경우 하나의 테이블로 가정
def merge_tables(cur_table, data):
    if data[-1][1] == 0: # 직전 데이터가 텍스트인 경우
        data.append([cur_table , 1])
        return
    
    elif data[-1][1] == 1: # 직전 테이터가 테이블인 경우
        row = 0
        while cur_table[row] == data[-1][0][row]:
            row+=1
        data[-1][0] += cur_table[row:]
        return 
    


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


            ## data에 append 할 때, text 면 label 0, table 이면 label 1 추가
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
                if text.strip():
                    data.append([text, 0])
                
                # table 추출
                padded_box = (box[0] - pad_size, box[1] - pad_size, box[2] + pad_size, box[3] + pad_size)
                page_in_table = page.within_bbox(padded_box)
                table = page_in_table.extract_table()
                if table:
                    merge_tables(table, data)                

                prev_table_box = box
            
            # 제일 아래 table 밑의 text 추출
            page_below_final_table = page.within_bbox((0,prev_table_box[3],page_width-1,page_height-1))
            

            # page number 및 footnote 글씨 크기 threshold로 제거
            threshold = 10 # pdf 특성에 맞게 조정   ``
            text = ""
            for char in page_below_final_table.chars:
                if char['size'] < threshold:
                    continue
                else:
                    text += str(char['text'])
            if text.strip():
                data.append([text, 0])


            # text = page_below_final_table.extract_text()
            
            # # page number 제거
            # text = re.sub(r"[0-9]+[A-Z]*-[0-9]+","",text)[:-1]
            # if text != "":
            #     data.append(text)

            
    path = f"./FTA_data/{pdf_path}"
    if not os.path.exists(path):
        os.makedirs(path)


    with open(f"{path}/text.txt", "w", encoding='utf-8') as wf:
        for d in data:
            text = str(d[0])
            if text.strip():
                wf.write(text+"\n")


extract_info(pdf_path)