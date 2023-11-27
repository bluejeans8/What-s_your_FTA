import os
import glob
import pdfplumber
import json

# PDF 정보
# 
# width 595.44
# height 841.68

# table 첫번째 column 빈칸채우기
def column_fill(table):
    prev_element = table[0]
    for element in table:
        if element[0] == '':
            element[0] = prev_element[0]
        prev_element = element        



# table을 data에 더해주기
def append_table(cur_table, data):        
    if data == [] or data[-1][1] == 0: # 첫 데이터 이거나, 직전 데이터가 텍스트인 경우
        column_fill(cur_table)
        data.append([cur_table , 1])
        return
    
    ## 테이블 병합 알고리즘:
    ## 두 테이블 사이에 텍스트가 껴 있는 경우 다른 테이블, 없는 경우 하나의 테이블로 가정
    elif data[-1][1] == 1: # 직전 테이터가 테이블인 경우
        row = 0
        while cur_table[row] == data[-1][0][row]:
            row+=1
            if row == len(data[-1][0]) or row == len(cur_table):
                break 
                
        data[-1][0] += cur_table[row:]
        column_fill(data[-1][0])
        return



# text를 data에 더해주기
def append_text(page, data, code):

    if code == '0': # 한
        size_threshold = 10
    elif code == '2': # 미
        size_threshold = 8 

    text = ""
    if code == '0' or code == '2': ## 한 or 미
        for char in page.chars:
            if char['size'] < size_threshold:
                continue
            else:
                text += str(char['text'])
    else: # 유
        words = page.extract_words(x_tolerance=1)
        for word in words:
            text += word['text'] + ' '
        
    if text.strip():
        data.append([text, 0])



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



# 열린 테이블(양 side가 막히지 않은 테이블) 검색
def find_open_table(page):
        
    page_update = page.within_bbox((0,70,page.width,page.height))

    lines = page_update.edges
    vertical = []
    horizontal = []
    v_threshold = 1
    h_threshold = 20
    for line in lines:
        if line['orientation'] == 'v':
            if line['bottom'] - line['top'] > v_threshold:
                vertical.append(line)
        elif line['orientation'] == 'h':
            if line['x1'] - line['x0'] > h_threshold:
                horizontal.append(line)

    if horizontal == [] or vertical == []:
        return None
    

    table_config = {        
        "vertical_strategy": "explicit",
        "horizontal_strategy": "explicit",
        "explicit_vertical_lines": (
            # Using both the left- and right-hand edges of each line
            [ x["x0"] for x in horizontal ]+
            [ x["x1"] for x in horizontal ]
        ),
        "explicit_horizontal_lines": (
            # Using both the top- and bottom-hand edges of each line
            [x["top"] for x in vertical] +
            [x["bottom"] for x in vertical]
        ),
        "join_tolerance": 50,
        "snap_tolerance": 5,
    }

    # table finding
    table = page.find_table(table_settings=table_config)
    table_content = page.extract_table(table_settings=table_config)

    #### Debug visually.
    # image = page.to_image(resolution=200)

    # image.reset().debug_tablefinder(table_config)

    # image.save("image.png", format="PNG")
    ####

    return table, table_content



def find_all_tables(page):

    # table이 포함된 boundary boxes 생성
    tables = []
    big_table = page.find_table()
    big_table_content = page.extract_table()

    if big_table != None: # 완전히 닫힌 table이 존재하는 경우
        bt_bounding_box = big_table.bbox
        if bt_bounding_box[3] - bt_bounding_box[1] > 600: # 페이지에 큰 표가 1개 존재하는 경우
            tables.append((bt_bounding_box, big_table_content))
        else: # 여러 표가 존재 or 작은 표가 1개 존재하는 경우
            t_locations = page.find_tables()
            tables_content = page.extract_tables()
            for t_location, table_content in zip(t_locations, tables_content):
                bounding_box = t_location.bbox
                tables.append((bounding_box, table_content))
    else: # 완전히 닫힌 table이 존재하지 않는 경우
        output = find_open_table(page)
        if output != None: # 열린 테이블이 존재하는 경우
            open_table, open_table_content = output
            ot_bounding_box = open_table.bbox
            tables.append((ot_bounding_box, open_table_content))

    return tables




def table_to_latex(data_path):
    with open(data_path,"r") as rf:
        for line in rf.readlines():
            if line.startswith('[['):
                line.replace("[['","").replace("']]","").replace("],[","&")
    return
    


# code: korea 0, EU 1, US 2
def extract_data(pdf_path, code):

    data = []

    with pdfplumber.open(pdf_path) as pdf:
        page_cnt = 0
        for page in pdf.pages:
            page_cnt += 1
            if page_cnt%200 == 0:
                print(page_cnt)

            tables = find_all_tables(page)

            page_width = page.width
            page_height = page.height
            page_header_height = 70
            prev_table_box = (0, page_header_height, page_width - 1, page_header_height)
            pad_size = 1


            ## data에 append 할 때, text 면 label 0, table 이면 label 1 추가
            for box, table_content in tables:

                if prev_table_box[3] >= box[1]: # 디버깅
                    # print("[debug]:", page_cnt, prev_table_box, box)
                    break
                
                # table 사이사이의 text 추출
                page_upward_table = page.within_bbox((0,prev_table_box[3],page_width-pad_size,box[1]))
                append_text(page_upward_table, data, code)

                if table_content:
                    append_table(table_content, data)                

                prev_table_box = box
            

            # 제일 아래 table 밑의 text 추출, page_number 제거
            if prev_table_box[3] < 750:
                if page_width < page_height: # 가로로 긴 pdf
                    page_number_height = 80
                    if page_height - page_number_height < prev_table_box[3]: # US에서 특수한 경우 예외처리
                        page_number_height = 30
                    page_number_width = 0
                else: # 세로로 긴 pdf
                    page_number_height = 0
                    page_number_width = 20
                
                page_below_final_table = page.within_bbox((0,prev_table_box[3],page_width-page_number_width,page_height-page_number_height))
                
                append_text(page_below_final_table, data, code)
        
    return data