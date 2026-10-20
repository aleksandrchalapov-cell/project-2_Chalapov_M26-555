import shlex

import prompt

from primitive_db.core import create_table, drop_table, list_tables
from primitive_db.utils import load_metadata, save_metadata

META_FILE = "db_meta.json"


def print_help():
    """Prints the help message for the current mode."""

    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")

    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")


def run():
    """Run the main command loop of the database."""
    print_help()
    while True:
        metadata = load_metadata(META_FILE)
        try:
            user_input = prompt.string(">>>Введите команду: ")
        except (KeyboardInterrupt, EOFError):
            print()
            break
        try:
            args = shlex.split(user_input)
        except ValueError:
            print(f"Некорректное значение: {user_input}. Попробуйте снова.\n")
            continue
        match args:
            case []:
                continue
            case ["create_table", table_name, *columns]:
                new_metadata = create_table(metadata, table_name, columns)
                if new_metadata is not None:
                    save_metadata(META_FILE, new_metadata)
            case ["drop_table", table_name]:
                new_metadata = drop_table(metadata, table_name)
                if new_metadata is not None:
                    save_metadata(META_FILE, new_metadata)
            case ["list_tables"]:
                list_tables(metadata)
            case ["help"]:
                print_help()
                continue
            case ["exit"]:
                break
            case ["create_table" | "drop_table" | "list_tables" | "help" | "exit", *_]:
                print(f"Некорректное значение: {user_input}. Попробуйте снова.")
            case [command, *_]:
                print(f"Функции {command} нет. Попробуйте снова.")
        print()
