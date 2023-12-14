import sys
import os
import utils

pdf_path = sys.argv[1]
code = sys.argv[2]


print(pdf_path)

data = utils.extract_data(pdf_path, code)

if code == "0":
    reg = "KOR"
elif code == "1":
    reg = "EU"
elif code == "2":
    reg = "US"

folder_name = pdf_path.split("/")[-1].split(".")[-2]
path = f"./FTA_data/{reg}/{folder_name}"
if not os.path.exists(path):
    os.makedirs(path)


with open(f"{path}/text.txt", "w", encoding='utf-8') as wf:
    for d in data:
        if isinstance(d[0], list):
            text = utils.to_latex(d[0])
            wf.write(text+"\n")
        else:
            text = str(d[0])
            if text.strip():
                wf.write(text+"\n")
