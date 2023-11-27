import sys
import os
import utils

data_path = sys.argv[1]
code = sys.argv[2]

print(data_path)

if code == "0":
    reg = "KOR"
elif code == "1":
    reg = "EU"
elif code == "2":
    reg = "US"

data = utils.table_to_latex(data_path)

folder_name = data_path.split("/")[-2]
path = f"./FTA_latex/{reg}/{folder_name}"
if not os.path.exists(path):
    os.makedirs(path)


with open(f"{path}/text.txt", "w", encoding='utf-8') as wf:
    for d in data:
        text = str(d[0])
        if text.strip():
            wf.write(text+"\n")