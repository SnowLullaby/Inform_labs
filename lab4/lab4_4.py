import time

words = ["type", "time", "evenWeek", "class", "building", "subject", "teacher", "lessonFormat"]


def fined_word(line, key_end_idx): # ищем значение
    idx = line.rfind('"')
    value_start_idx = line[key_end_idx + 1:].find('"') + key_end_idx + 1
    return line[value_start_idx + 1:idx]


def parse_pair(line, key_string, key_end_idx):  # обрабатываем каждую строку отдельно
    replacement_symbols = {"<": "&lt;", ">": "&gt;", '"': "&quot;"}
    word = fined_word(line, key_end_idx)

    # replace all special symbols
    for symbol, replacement in replacement_symbols.items():
        word = word.replace(symbol, replacement)
    return key_string, word


class Schedule:  # создаем конструктор класса для более удобной работы
    def __init__(self):
        self.day = ""
        self.lessons = []


def get_indexes_of_escaped(string):  # вот тут ищем индексы экранированных кавычек
    escaped_indexes = []
    for i in range(len(string) - 1):
        if string[i] == '\\' and string[i + 1] == '"':
            escaped_indexes.append(i + 1)
    return escaped_indexes


def del_escaped_from_key(key_string):  # удаляем все ненужное из ключа
    j = 0
    while key_string[j] == "\\": j += 1
    new_key = key_string[j]
    for i in range(j+1, len(key_string)):
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
        if '"' in line:
            key_begin_idx = line.find('"')  # key begin
            escaped_indexes = get_indexes_of_escaped(line)

            key_end_idx = line[key_begin_idx + 1:].find('"') + key_begin_idx + 1  # key end
            while key_end_idx in escaped_indexes:
                key_end_idx = line[key_end_idx + 1:].find('"') + key_end_idx + 1  # key end

            if line.count('"') - len(escaped_indexes) == 4:
                has_value = True

            key_string = line[key_begin_idx + 1:key_end_idx]
            key_string = del_escaped_from_key(key_string)

        counter_tt += line.count("{") - line.count("}") - key_string.count("{") + key_string.count("}")
        counter_les += line.count("[") - line.count("]") - key_string.count("[") + key_string.count("]")

        if has_value:
            counter_tt += - fined_word(line, key_end_idx).count("{") + fined_word(line, key_end_idx).count("}")
            counter_les += - fined_word(line, key_end_idx).count("[") + fined_word(line, key_end_idx).count("]")

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
            key, word = parse_pair(line, key_string, key_end_idx)
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
                "{") - key_string.count("{") - fined_word(line, key_end_idx).count("{") > 0):
            in_lesson = True

        if in_lesson and has_value:
            key, word = parse_pair(line, key_string, key_end_idx)
            if key in words:
                lesson[key] = word

        if (line.count("}") - key_string.count("}") > 0 and not has_value) or (has_value and line.count(
                "}") - key_string.count("}") - fined_word(line, key_end_idx).count("}") > 0):
            in_lesson = False
            schedule.lessons.append(lesson)
            lesson = dict()

    return schedule


def file_to_textile(file):
    schedule = parse_file(file)
    resulting_string = ""
    resulting_string += f"{schedule.day}\n"
    for lesson in schedule.lessons:
        for value in lesson.values():
            resulting_string += f"{value}\n"
    return resulting_string


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


start_time = time.perf_counter()
for n in range(10):
    input_file_name = "template"
    output_file_name = "timetable"

    with open(input_file_name + ".json", 'r', encoding='utf-8') as f:
        xml = file_to_textile(prepare_file(f))

    # запись в файл
    with open(output_file_name + ".textile", 'w', encoding="utf-8") as f:
        f.write(xml)

print(f'time:  {time.perf_counter()-start_time}')
