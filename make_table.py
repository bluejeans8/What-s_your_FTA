import pdfplumber

pdf_path = "/home/jsk0821/Documents/FTA/FTA_pdfs/US/merged_US_text_of_agreement_eng__Australia Free Trade Agreement__20040518.pdf"



with pdfplumber.open(pdf_path) as pdf:

    page = pdf.pages[616]

    # im = page.to_image()
    # im.reset().debug_tablefinder({
    #     "vertical_strategy": "lines",
    #     "horizontal_strategy":"text",
    #     "join_tolerance": 50,
    # })

    table = page.extract_table()

    print(table)

    lines = page.edges

    # Debug visually.
    image = page.to_image(resolution=200)

    image.reset().debug_tablefinder({
        "vertical_strategy": "explicit",
        "explicit_vertical_lines": (
            # Using both the left- and right-hand edges of each line
            [ x["x0"] for x in lines ] +
            [ x["x1"] for x in lines ]
        ),
        "horizontal_strategy": "lines",
        "join_tolerance": 50,
        "snap_tolerance": 5,
    })


    image.save("image.png", format="PNG")
