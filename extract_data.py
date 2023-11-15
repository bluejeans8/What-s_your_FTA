import pandas as pd
import os
import pdfplumber
import glob
import re


# PDF 정보
# 
# width 595.44
# height 841.68


## 테이블 병합 알고리즘:
## 두 테이블 사이에 텍스트가 껴 있는 경우 다른 테이블, 없는 경우 하나의 테이블로 가정
def merge_tables(cur_table, data):        
    if data == [] or data[-1][1] == 0: # 첫 데이터 이거나, 직전 데이터가 텍스트인 경우
        data.append([cur_table , 1])
        return
    
    elif data[-1][1] == 1: # 직전 테이터가 테이블인 경우
        row = 0
        while cur_table[row] == data[-1][0][row]:
            row+=1
            if row == len(data[-1][0]) or row == len(cur_table):
                break 
                
        data[-1][0] += cur_table[row:]
        return 
    


def extract_info(pdf_path):

    table, text = "", ""

    data = []

    with pdfplumber.open(pdf_path) as pdf:
        page_cnt = 0
        for page in pdf.pages:
            page_cnt += 1
            if page_cnt%200 == 0:
                print(page_cnt)

            # table이 포함된 boundary boxes 생성
            boxes = []
            big_table = page.find_table()

            if big_table != None:
                bt_bounding_box = big_table.bbox
                if bt_bounding_box[3] - bt_bounding_box[1] > 600:
                    boxes.append(bt_bounding_box)
                
                else:
                    t_locations = page.find_tables()
                    for t_location in t_locations:
                        bounding_box = t_location.bbox
                        boxes.append(bounding_box)    

            page_width = page.width
            page_height = page.height
            prev_table_box = (0,0,page_width - 1,0)
            pad_size = 1


            ## data에 append 할 때, text 면 label 0, table 이면 label 1 추가
            for box in boxes:

                if prev_table_box[3] >= box[1]: # 디버깅
                    # print("[debug]:", page_cnt, prev_table_box, box)
                    break

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
            
            # 제일 아래 table 밑의 text 추출, page_number 제거
            if prev_table_box[3] < 750:
                if page_width < page_height: # 가로로 긴 pdf
                    page_number_height = 80
                    page_number_width = 0
                else: # 세로로 긴 pdf
                    page_number_height = 0
                    page_number_width = 20
                
                page_below_final_table = page.within_bbox((0,prev_table_box[3],page_width-page_number_width,page_height-page_number_height))


                # footnote 글씨 크기 threshold로 제거
                size_threshold = 10 # pdf 특성에 맞게 조정   ``
                text = ""
                for char in page_below_final_table.chars:
                    if char['size'] < size_threshold:
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

    folder_name = pdf_path.split("/")[-1].split(".")[-2]
    path = f"./FTA_data/{folder_name}"
    if not os.path.exists(path):
        os.makedirs(path)


    with open(f"{path}/text.txt", "w", encoding='utf-8') as wf:
        for d in data:
            text = str(d[0])
            if text.strip():
                wf.write(text+"\n")


# paths = glob.glob("C:/Users/User/What-s_your_FTA/FTA_pdfs/*")

paths = ['C:/Users/User/What-s_your_FTA/FTA_pdfs/RCEP.pdf', 'C:/Users/User/What-s_your_FTA/FTA_pdfs/text_of_agreement_eng_한,EU FTA.pdf', 'C:/Users/User/What-s_your_FTA/FTA_pdfs/text_of_agreement_eng_한,중 FTA.pdf', 'C:/Users/User/What-s_your_FTA/FTA_pdfs/text_of_agreement_eng_한-ASEAN_FTA.pdf', 'C:/Users/User/What-s_your_FTA/FTA_pdfs/text_of_agreement_eng_한-EFTA_FTA.pdf', 'C:/Users/User/What-s_your_FTA/FTA_pdfs/text_of_agreement_eng_한-뉴질랜드_FTA.pdf', 'C:/Users/User/What-s_your_FTA/FTA_pdfs/text_of_agreement_eng_한-베트남_FTA.pdf', 'C:/Users/User/What-s_your_FTA/FTA_pdfs/text_of_agreement_eng_한-싱가포르_DPA.pdf', 'C:/Users/User/What-s_your_FTA/FTA_pdfs/text_of_agreement_eng_한-싱가포르_FTA.pdf', 'C:/Users/User/What-s_your_FTA/FTA_pdfs/text_of_agreement_eng_한-인도_CEPA.pdf', 'C:/Users/User/What-s_your_FTA/FTA_pdfs/text_of_agreement_eng_한-칠레_FTA.pdf', 'C:/Users/User/What-s_your_FTA/FTA_pdfs/text_of_agreement_eng_한-캐나다_FTA.pdf', 'C:/Users/User/What-s_your_FTA/FTA_pdfs/text_of_agreement_eng_한-콜롬비아_FTA.pdf', 'C:/Users/User/What-s_your_FTA/FTA_pdfs/text_of_agreement_eng_한-터키_FTA.pdf', 'C:/Users/User/What-s_your_FTA/FTA_pdfs/text_of_agreement_eng_한-페루_FTA.pdf', 'C:/Users/User/What-s_your_FTA/FTA_pdfs/text_of_agreement_eng_한-호주_FTA.pdf', 'C:/Users/User/What-s_your_FTA/FTA_pdfs/text_of_agreement_eng_한미FTA.pdf', 'C:/Users/User/What-s_your_FTA/FTA_pdfs/한-영 FTA.pdf', 'C:/Users/User/What-s_your_FTA/FTA_pdfs/한-이스라엘 FTA.pdf', 'C:/Users/User/What-s_your_FTA/FTA_pdfs/한-인도네시아 FTA.pdf', 'C:/Users/User/What-s_your_FTA/FTA_pdfs/한-캄보디아 FTA.pdf', 'C:/Users/User/What-s_your_FTA/FTA_pdfs/한-튀르키예 FTA.pdf', 'C:/Users/User/What-s_your_FTA/FTA_pdfs/한-중미 FTA-1.pdf', 'C:/Users/User/What-s_your_FTA/FTA_pdfs/한-중미 FTA-2.pdf']



for pdf_path in paths[22:]:
    print(pdf_path)
    extract_info(pdf_path)


# extract_info("C:/Users/User/What-s_your_FTA/FTA_pdfs/text_of_agreement_eng_한-인도_CEPA.pdf")