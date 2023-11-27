import pdfplumber

# pdf_path = ".\\FTA_pdfs\\EU\\EU_agreement_Antigua and Barbuda (CARIFORUM)_20110225.pdf"

pdf_path = "/home/jsk0821/Documents/FTA/FTA_pdfs/EU/EU_agreement_Madagascar (ESA)_20120424.pdf"


def extract_table():
    # for table extraction

    with pdfplumber.open(pdf_path) as pdf:

        page = pdf.pages[165]
        
        page_update = page.within_bbox((0,0,page.width,page.height))
        
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
            print("no table")
            return
        

        table_config = {        
            "vertical_strategy": "explicit",
            "horizontal_strategy": "explicit",
            "explicit_vertical_lines": (
                # Using both the left- and right-hand edges of each line
                [ x["x0"] for x in horizontal ]+
                [ x["x1"] for x in horizontal ]
            ),
            "explicit_horizontal_lines": (
                # Using both the left- and right-hand edges of each line
                [x["top"] for x in vertical] +
                [x["bottom"] for x in vertical]
            ),
            "join_tolerance": 50,
            "snap_tolerance": 5,
        }

        # table extraction
        table = page.extract_table(table_settings=table_config)

        ##### Debug visually.
        image = page.to_image(resolution=200)

        image.reset().debug_tablefinder(table_config)

        image.save("image.png", format="PNG")
        #####

        # # table 첫번째 column 빈칸채우기
        # for element in table:
        #     if element[0] == '':
        #         element[0] = prev_element[0]
        #     prev_element = element

        print(table)

        return 


extract_table()