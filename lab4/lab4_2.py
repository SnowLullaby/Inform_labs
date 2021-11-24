import json
import xmltodict


def file_to_xml(file):
    to_xml = xmltodict.unparse(file, pretty=True)
    return to_xml


input_file_name = "template"
output_file_name = "timetable"

with open(input_file_name + ".json", 'r', encoding='utf-8') as f:
    xml = file_to_xml(json.load(f))

# запись в файл
with open(output_file_name + ".xml", 'w', encoding="utf-8") as f:
    f.write(xml)

