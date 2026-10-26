"""лабораторная работа 1: поиск по каталогу аэропортов

Вариант: airports-csv | title | fold | words-all | best | plain | none"""

import csv
import os
import shlex
import time


# названия столбцов из файла records.csv
FIELDS = [
    "id", "title", "city", "keywords", "country", "kind",
    "elevation_ft", "latitude", "longitude", "scheduled", "url"
]

# поля, по которым разрешена фильтрация
STRING_FILTERS = ["country", "kind"]
NUMBER_FILTERS = ["elevation_ft", "latitude", "longitude"]
BOOL_FILTERS = ["scheduled"]


# переменные хранят текущее состояние программы
records = [] # хранятся загруженные записи
loaded = False # признак загрузки
filters = [] # добавленные фильтры
last_output = "" # последний результат для сохранения


def read_csv(filename):
    """прочитать CSV и вернуть список словарей с аэропортами"""
    result = []

    # with сам закроет файл после завершения работы
    with open(filename, encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)

        if reader.fieldnames is None:
            raise ValueError("Файл пустой или не является CSV")

        # проверяем, что в файле есть нужные столбцы
        for field in FIELDS:
            if field not in reader.fieldnames:
                raise ValueError("В CSV нет поля: " + field)

        # reader по очереди отдаёт строки CSV в виде словарей
        for row in reader:
        # в CSV всё читается как текст. числа превращаем в float
            for field in NUMBER_FILTERS:
                if row[field] == "":
                    row[field] = None
                else:
                    row[field] = float(row[field])

            # true и false превращаем в логические значения True и False
            if row["scheduled"] == "":
                row["scheduled"] = None
            else:
                row["scheduled"] = row["scheduled"].casefold() == "true"

            result.append(row)

    return result


def get_file_path(filename):
    """найти CSV рядом с программой или в папке data/airports"""
    possible_paths = []
    program_folder = os.path.dirname(__file__)

    possible_paths.append(filename)
    possible_paths.append(os.path.join(program_folder, filename))
    possible_paths.append(
        os.path.join(program_folder, "data", "airports", os.path.basename(filename))
    )

    # можно написать и records.csv, и airports.csv
    if os.path.basename(filename) in ["records.csv", "airports.csv"]:
        possible_paths.append(
            os.path.join(program_folder, "data", "airports", "records.csv")
        )

    for path in possible_paths:
        if os.path.isfile(path):
            return path

    raise ValueError("Файл не найден: " + filename)


def show_value(value):
    """сделать значение понятным для вывода в карточке"""
    if value is None or value == "":
        return "-"
    if value is True:
        return "true"
    if value is False:
        return "false"
    return str(value)


def get_filter_value(field, text):
    """превратить текст команды в значение нужного типа"""
    if field in NUMBER_FILTERS:
        try:
            return float(text)
        except ValueError:
            raise ValueError("Для поля " + field + " нужно число")

    if field in BOOL_FILTERS:
        if text.casefold() == "true":
            return True
        if text.casefold() == "false":
            return False
        raise ValueError("Для поля scheduled нужно true или false")

    return text


def record_passes_filter(record, one_filter):
    """проверить, подходит ли один аэропорт под один фильтр"""
    field = one_filter[0]
    operator = one_filter[1]
    needed_value = one_filter[2]
    actual_value = record[field]

    # пустое значение по ТЗ не проходит фильтр
    if actual_value is None or actual_value == "":
        return False

    # текстовые фильтры тоже не учитывают регистр
    if field in STRING_FILTERS:
        actual_value = actual_value.casefold()
        needed_value = needed_value.casefold()

    if operator == "eq":
        return actual_value == needed_value
    if operator == "ne":
        return actual_value != needed_value
    if operator == "contains":
        return needed_value in actual_value
    if operator == "lt":
        return actual_value < needed_value
    if operator == "le":
        return actual_value <= needed_value
    if operator == "gt":
        return actual_value > needed_value
    if operator == "ge":
        return actual_value >= needed_value

    return False


def record_passes_all_filters(record):
    """вернуть True, только если запись проходит каждый фильтр"""
    for one_filter in filters:
        if not record_passes_filter(record, one_filter):
            return False
    return True


def search_records(query):
    """найти записи по title: все слова запроса должны быть в названии"""
    query_words = query.casefold().split()
    found_count = 0
    best_item = None
    started = time.time()

    for record in records:
        if not record_passes_all_filters(record):
            continue

        # в варианте fold регистр не важен. В варианте title ищем только в title
        title_words = record["title"].casefold().split()

        # пустой запрос не ищет текст, а оставляет только работу фильтров
        if query_words == []:
            relevance = 0.0
        else:
            every_word_found = True

            # words-all: каждое слово запроса должно быть среди слов названия
            for word in query_words:
                if word not in title_words:
                    every_word_found = False

            if not every_word_found:
                continue

            # чем короче название при одинаковом запросе, тем выше релевантность
            relevance = len(query_words) / len(title_words)

        found_count += 1

        # best: запоминаем запись, если она первая или лучше прежней лучшей
        if best_item is None or relevance > best_item[0]:
            best_item = [relevance, record]

    elapsed = (time.time() - started) * 1000
    return best_item, found_count, elapsed


def make_card_text(record, relevance=None):
    """собрать полную карточку аэропорта в одну строку текста"""
    lines = []
    lines.append("[" + record["id"] + "] " + show_value(record["title"]))

    # по ТЗ в карточке печатаем все поля, кроме уже выведенных id и title
    for field in FIELDS:
        if field == "id" or field == "title":
            continue
        lines.append("  " + field + ": " + show_value(record[field]))

    if relevance is not None:
        lines.append("  Релевантность: {:.2f}".format(relevance))

    return "\n".join(lines)


def print_help():
    """напечатать команды, которые есть в данном варианте"""
    print("""Команды:
  help                                      список команд
  load <файл>                               загрузить CSV
  show                                      показать все записи
  fields                                    показать поля и фильтры
  filter add <поле> <оператор> <значение>  добавить фильтр
  filter list                               показать фильтры
  filter remove <номер>                     удалить фильтр
  filter clear                              удалить все фильтры
  search \"<запрос>\"                        выполнить поиск
  save <файл>                               сохранить последнюю выдачу
  exit                                      завершить программу

Вариант: airports-csv | title | fold | words-all | best | plain | none""")


def command_load(parts):
    """выполнить команду load"""
    global records, loaded, filters, last_output

    if len(parts) != 2:
        print("Ошибка: Использование: load <файл>")
        return

    if not parts[1].casefold().endswith(".csv"):
        print("Ошибка: Поддерживаются только файлы формата .csv")
        return

    filename = get_file_path(parts[1])
    records = read_csv(filename)
    loaded = True

    # новая загрузка по ТЗ сбрасывает старые настройки и выдачу
    filters = []
    last_output = ""

    print("Загружено записей:", len(records))


def command_fields():
    """показать поля, их типы и допустимые операторы фильтрации"""
    print("Поиск по полю: title")
    print()
    print("Поле          Тип    Фильтры")
    print("------------  -----  -----------------")

    for field in FIELDS:
        if field in STRING_FILTERS:
            print("{:<13} str    eq ne contains".format(field))
        elif field in NUMBER_FILTERS:
            print("{:<13} float  eq ne lt le gt ge".format(field))
        elif field in BOOL_FILTERS:
            print("{:<13} bool   eq ne".format(field))
        else:
            print("{:<13} str    -".format(field))

    print()
    print("eq = равно; ne = не равно; contains = содержит текст.")
    print("lt <; le <=; gt >; ge >=. true = да; false = нет.")


def command_filter(parts):
    """выполнить filter add, list, remove или clear"""
    global filters

    if len(parts) < 2:
        print("Ошибка: Использование: filter add, list, remove или clear")
        return

    action = parts[1]

    if action == "list" and len(parts) == 2:
        if filters == []:
            print("Фильтров нет")
        else:
            for number, one_filter in enumerate(filters, 1):
                print("{}. {} {} {}".format(
                    number,
                    one_filter[0],
                    one_filter[1],
                    show_value(one_filter[2])
                ))
        return

    if action == "clear" and len(parts) == 2:
        filters = []
        print("Фильтры удалены")
        return

    if action == "remove" and len(parts) == 3:
        try:
            number = int(parts[2])
        except ValueError:
            print("Ошибка: Номер фильтра должен быть целым числом")
            return

        if number < 1 or number > len(filters):
            print("Ошибка: Фильтра с таким номером нет")
            return

        filters.pop(number - 1)
        print("Фильтр удалён")
        return

    if action == "add" and len(parts) == 5:
        field = parts[2]
        operator = parts[3]
        text_value = parts[4]

        if field not in STRING_FILTERS + NUMBER_FILTERS + BOOL_FILTERS:
            print("Ошибка: Поле не поддерживает фильтрацию")
            return

        if field in STRING_FILTERS:
            allowed_operators = ["eq", "ne", "contains"]
        elif field in NUMBER_FILTERS:
            allowed_operators = ["eq", "ne", "lt", "le", "gt", "ge"]
        else:
            allowed_operators = ["eq", "ne"]

        if operator not in allowed_operators:
            print("Ошибка: Неподходящий оператор для поля " + field)
            return

        try:
            value = get_filter_value(field, text_value)
        except ValueError as error:
            print("Ошибка:", error)
            return

        filters.append([field, operator, value])
        print("Добавлен фильтр {}: {} {} {}".format(
            len(filters), field, operator, show_value(value)
        ))
        return

    print("Ошибка: Использование: filter add <поле> <оператор> <значение>")


def command_show():
    """вывести все записи без поиска и без фильтров"""
    global last_output

    cards = []

    print("Записей:", len(records))
    for record in records:
        card = make_card_text(record)
        print()
        print(card)
        cards.append(card)

    last_output = "Записей: " + str(len(records)) + "\n\n" + "\n\n".join(cards)


def command_search(parts):
    """выполнить команду search и показать одну лучшую запись"""
    global last_output

    if len(parts) != 2:
        print('Ошибка: Использование: search "<запрос>"')
        return

    best_item, found_count, elapsed = search_records(parts[1])

    # best: из всех найденных записей показываем только одну лучшую
    if best_item is None:
        shown = []
    else:
        shown = [best_item]

    cards = []

    print("Найдено: {}; показано: {}".format(found_count, len(shown)))

    for item in shown:
        relevance = item[0]
        record = item[1]
        card = make_card_text(record, relevance)

        cards.append(card)

        print()
        print(card)

    last_output = "Найдено: {}; показано: {}\n".format(found_count, len(shown))
    if cards != []:
        last_output += "\n" + "\n\n".join(cards) + "\n"
    last_output += "\nВремя поиска: {:.2f} мс".format(elapsed)

    print("\nВремя поиска: {:.2f} мс".format(elapsed))


def command_save(parts):
    """сохранить последнюю выдачу в текстовый файл"""
    if len(parts) != 2:
        print("Ошибка: Использование: save <файл>")
        return

    if last_output == "":
        print("Ошибка: Сначала выполните show или search")
        return

    with open(parts[1], "w", encoding="utf-8") as file:
        file.write(last_output + "\n")

    print("Сохранено:", parts[1])


def main():
    """запустить цикл ввода команд"""
    print("Поиск по каталогу аэропортов. Команды: help. Выход: exit.")

    while True:
        try:
            # shlex.split понимает кавычки в запросах из нескольких слов
            parts = shlex.split(input("\nsearch> "))
        except ValueError as error:
            print("Ошибка:", error)
            continue
        except EOFError:
            print()
            break

        if parts == []:
            continue

        command = parts[0]

        if command == "exit":
            break
        if command == "help":
            print_help()
            continue

        # до load по ТЗ доступны только help, load и exit
        if not loaded:
            if command == "load":
                try:
                    command_load(parts)
                except (OSError, ValueError) as error:
                    print("Ошибка:", error)
            else:
                print("Ошибка: Сначала загрузите данные командой load <файл>")
            continue

        try:
            if command == "load":
                command_load(parts)
            elif command == "show" and len(parts) == 1:
                command_show()
            elif command == "fields" and len(parts) == 1:
                command_fields()
            elif command == "filter":
                command_filter(parts)
            elif command == "search":
                command_search(parts)
            elif command == "save":
                command_save(parts)
            else:
                print("Ошибка: Неизвестная команда. Введите help")
        except (OSError, ValueError) as error:
            print("Ошибка:", error)


if __name__ == "__main__":
    main()
