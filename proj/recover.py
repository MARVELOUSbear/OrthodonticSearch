import json
from io import BytesIO

from lxml import etree

dir = "data/fulldata2.xml"

with open(dir, "rb") as f:
    xml = f.read()
parser = etree.XMLParser(encoding='utf-8', recover=True)
tree = etree.parse(BytesIO(xml), parser)
root = tree.getroot()
data = []
count = 0
date_dict = {"Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04", "May": "05", "Jun": "06", "Jul": "07", "Aug": "08",
             "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12"}
for item in root.getchildren():
    item_data = {}
    flag = False
    for elem in item.getchildren():
        if elem.tag == "date":
            date = elem.text.strip("-")
            for key in date_dict.keys():
                date = date.replace(key, date_dict[key])
            item_data["date"] = date
        elif elem.tag == "authors":
            item_data["authors"] = []
            for author in elem.getchildren():
                if author.text:
                    item_data["authors"].append(t)
        elif elem.tag == "abstract":
            if not elem.text:
                flag = True
                item_data["abstract"] = ""
            else:
                item_data["abstract"] = elem.text
        else:
            item_data[elem.tag] = elem.text
    count += 1
    data.append(item_data)

print(count)
with open("data/fulljson2.json", "w") as write_file:
    json.dump(data, write_file, indent=4)
