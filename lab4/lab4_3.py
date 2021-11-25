"""
Дополнительное задание №2 к лабораторной работе №4
Версия от 13:40 25.11

"""

import re
words = ["type", "time", "evenWeek", "class", "building", "subject", "teacher", "lessonFormat"]


def parse_pair(word):  # обрабатываем каждую строку отдельно
    replacement_symbols = {"<": "&lt;", ">": "&gt;", '"': "&quot;"}

    # replace all special symbols
    for symbol, replacement in replacement_symbols.items():
        word = word.replace(symbol, replacement)
    return word


class Schedule:  # создаем конструктор класса для более удобной работы
    def __init__(self):
        self.day = ""
        self.lessons = []


def del_escaped_from_key(key_string):  # удаляем все \ и экраннированные символы из ключа и все исключения
    j = 0
    while key_string[j] == "\\": j += 1
    new_key = key_string[j]
    for i in range(j + 1, len(key_string)):
        if key_string[i] != "\\" and key_string[i - 1] != "\\":
            new_key += key_string[i]
    replacement_symbols = {"<": "", ">": "", '"': ""}
    for symbol, replacement in replacement_symbols.items():
        new_key = new_key.replace(symbol, replacement)
    return new_key


def parse_file(file):  # основная функция для парсинга
    schedule = Schedule()
    lesson = dict()
    begin_of_timetable = False
    begin_of_lessons = False
    in_lesson = False
    counter_les = 0
    counter_tt = 0

    for line in file:
        key_string = ''
        has_value = False
        word = ''
        key_pattern = r'\"(.*?[^\\])\"'
        pair_pattern = r'\"(.*?[^\\])\"\s*:\s*\"(.*?[^\\])\"'

        if re.search(pair_pattern, line) is not None:
            key_string, word = re.findall(key_pattern, line)
            has_value = True
        if re.search(key_pattern, line) is not None:
            key_string = del_escaped_from_key(re.search(key_pattern, line)[0])

        counter_tt += line.count("{") - line.count("}") - key_string.count("{") + key_string.count("}")
        counter_les += line.count("[") - line.count("]") - key_string.count("[") + key_string.count("]")

        if has_value:
            counter_tt += - word.count("{") + word.count("}")
            counter_les += - word.count("[") + word.count("]")

        if key_string == "timetable" and not has_value:
            begin_of_timetable = True
            counter_tt = line.count("{") - key_string.count("{")
            continue

        if not begin_of_timetable:
            continue

        if counter_tt == 0:  # проверяем не закончился ли блок timetable
            begin_of_timetable = False
            break

        if key_string == 'day' and has_value and not begin_of_lessons:  # если найден день
            word = parse_pair(word)
            schedule.day = word
            continue

        if key_string == 'lessons' and not has_value:  # если мы нашли блок с уроками
            begin_of_lessons = True
            counter_les = line.count("[") - key_string.count("[")
            continue

        if not begin_of_lessons:
            continue

        if counter_les == 0:
            begin_of_lessons = False
            break

        if (line.count("{") - key_string.count("{") > 0 and not has_value) or (has_value and line.count(
                "{") - key_string.count("{") - word.count("{") > 0):
            in_lesson = True

        if in_lesson and has_value:
            word = parse_pair(word)
            if key_string in words:
                lesson[key_string] = word

        if (line.count("}") - key_string.count("}") > 0 and not has_value) or (has_value and line.count(
                "}") - key_string.count("}") - word.count("}") > 0):
            in_lesson = False
            schedule.lessons.append(lesson)
            lesson = dict()

    return schedule


def file_to_xml(file):
    schedule = parse_file(file)
    xml = "<timetable>\n"
    xml += f"\t<day>{schedule.day}</day>\n"
    for i, lesson in enumerate(schedule.lessons):
        xml += f"\t<lesson{i + 1}>\n"
        for p, value in lesson.items():
            xml += f"\t\t<{p}>{value}</{p}>\n"
        xml += f"\t</lesson{i + 1}>\n"
    xml += "</timetable>"
    return xml


def prepare_file(file):
    lines = file.readlines()
    line = " ".join(lines)
    new_file = []
    count_qm = 0
    key_start_idx = 0
    st_idx = 0
    if '"' in line:
        for i in range(len(line)):
            if line[i] == '"' and count_qm == 0:
                count_qm += 1
                key_start_idx = i
                break
        for i in range(key_start_idx + 1, len(line)):
            if line[i] == '"' and line[i - 1] != "\\":
                count_qm += 1
            if (line[i] == '{' or line[i] == '[' or line[i] == ',' or line[i] == '}' or line[i] == ']') and count_qm % 2 == 0:
                end_idx = i
                new_file.append(line[st_idx: end_idx + 1])
                st_idx = i + 1

        new_file.append(line[st_idx:])
    return new_file


input_file_name = "template"
output_file_name = "timetable"

with open(input_file_name + ".json", 'r', encoding='utf-8') as f:
    xml = file_to_xml(prepare_file(f))

# запись в файл
with open(output_file_name + ".xml", 'w', encoding="utf-8") as f:
    f.write(xml)
