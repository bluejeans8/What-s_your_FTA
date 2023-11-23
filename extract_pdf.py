import sys
import os
import utils

pdf_path = sys.argv[1]

data = utils.extract_data(pdf_path)

folder_name = pdf_path.split("/")[-1].split(".")[-2]
path = f"./FTA_data/EU/{folder_name}"
if not os.path.exists(path):
    os.makedirs(path)


with open(f"{path}/text.txt", "w", encoding='utf-8') as wf:
    for d in data:
        text = str(d[0])
        if text.strip():
            wf.write(text+"\n")
