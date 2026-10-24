import prompt
from prettytable import PrettyTable

from primitive_db.core import (
    check_table,
    create_table,
    delete,
    drop_table,
    insert,
    list_tables,
    matches,
    select,
    table_info,
    update,
    validate_clause,
)
from primitive_db.decorators import create_cacher, handle_db_errors
from primitive_db.parser import (
    parse_condition,
    parse_set,
    parse_values,
    split_where,
    tokenize,
)
from primitive_db.utils import (
    delete_table_data,
    load_metadata,
    load_table_data,
    save_metadata,
    save_table_data,
)

META_FILE = "db_meta.json"
COMMANDS = (
    "create_table",
    "list_tables",
    "drop_table",
    "insert",
    "select",
    "update",
    "delete",
    "info",
    "exit",
    "help",
)
select_cache = create_cacher()


def print_help():
    """Prints the help message for the current mode."""

    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")

    print("\n***Операции с данными***")
    print("Функции:")
    print(
        "<command> insert into <имя_таблицы> values "
        "(<значение1>, <значение2>, ...) - создать запись."
    )
    print(
        "<command> select from <имя_таблицы> where <столбец> = <значение> "
        "- прочитать записи по условию."
    )
    print("<command> select from <имя_таблицы> - прочитать все записи.")
    print(
        "<command> update <имя_таблицы> set <столбец1> = <новое_значение1> "
        "where <столбец_условия> = <значение_условия> - обновить запись."
    )
    print(
        "<command> delete from <имя_таблицы> where <столбец> = <значение> "
        "- удалить запись."
    )
    print("<command> info <имя_таблицы> - вывести информацию о таблице.")

    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")


def print_records(metadata, table_name, records):
    """Print records as a table with the columns of the schema."""
    if not records:
        print("Записи не найдены.")
        return
    columns = list(metadata[table_name])
    table = PrettyTable(columns)
    for record in records:
        table.add_row([record[column] for column in columns])
    print(table)


def save_records(table_name, table_data):
    """Save the records of a table and forget the cached select results."""
    save_table_data(table_name, table_data)
    select_cache.clear()


@handle_db_errors
def run_drop(metadata, table_name):
    """Drop an existing table after confirmation, together with its records."""
    check_table(metadata, table_name)
    new_metadata = drop_table(metadata, table_name)
    if new_metadata is None:
        return
    save_metadata(META_FILE, new_metadata)
    delete_table_data(table_name)
    select_cache.clear()


@handle_db_errors
def run_select(metadata, table_name, where_clause):
    """Print the records that match the where clause (all if it is None)."""
    validate_clause(metadata, table_name, where_clause or {})
    key = (table_name, str(where_clause))
    records = select_cache(
        key, lambda: select(load_table_data(table_name), where_clause)
    )
    print_records(metadata, table_name, records)


@handle_db_errors
def run_update(metadata, table_name, set_clause, where_clause):
    """Update the records that match the where clause and report their IDs."""
    if "ID" in set_clause:
        raise ValueError('Ошибка: Столбец "ID" нельзя изменить.')
    validate_clause(metadata, table_name, set_clause)
    validate_clause(metadata, table_name, where_clause)
    table_data = load_table_data(table_name)
    ids = [record["ID"] for record in table_data if matches(record, where_clause)]
    if not ids:
        print("Записи не найдены.")
        return
    save_records(table_name, update(table_data, set_clause, where_clause))
    for record_id in ids:
        print(f'Запись с ID={record_id} в таблице "{table_name}" успешно обновлена.')


@handle_db_errors
def run_delete(metadata, table_name, where_clause):
    """Delete the records that match the where clause and report their IDs."""
    validate_clause(metadata, table_name, where_clause)
    table_data = load_table_data(table_name)
    ids = [record["ID"] for record in table_data if matches(record, where_clause)]
    if not ids:
        print("Записи не найдены.")
        return
    new_data = delete(table_data, where_clause)
    if new_data is None:
        return
    save_records(table_name, new_data)
    for record_id in ids:
        print(f'Запись с ID={record_id} успешно удалена из таблицы "{table_name}".')


def execute(metadata, tokens):
    """Run one database command; raise ValueError if it cannot be parsed."""
    match tokens:
        case ["create_table", table_name, *columns]:
            new_metadata = create_table(metadata, table_name, columns)
            if new_metadata is not None:
                save_metadata(META_FILE, new_metadata)
        case ["drop_table", table_name]:
            run_drop(metadata, table_name)
        case ["list_tables"]:
            list_tables(metadata)
        case ["insert", "into", table_name, "values", *values]:
            table_data = insert(metadata, table_name, parse_values(values))
            if table_data is not None:
                save_records(table_name, table_data)
        case ["select", "from", table_name]:
            run_select(metadata, table_name, None)
        case ["select", "from", table_name, "where", *condition]:
            run_select(metadata, table_name, parse_condition(condition))
        case ["update", table_name, "set", *clauses]:
            set_tokens, where_tokens = split_where(clauses)
            set_clause = parse_set(set_tokens)
            where_clause = parse_condition(where_tokens)
            run_update(metadata, table_name, set_clause, where_clause)
        case ["delete", "from", table_name, "where", *condition]:
            run_delete(metadata, table_name, parse_condition(condition))
        case ["info", table_name]:
            table_info(metadata, table_name)
        case [command, *_] if command in COMMANDS:
            raise ValueError
        case [command, *_]:
            print(f"Функции {command} нет. Попробуйте снова.")


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
            tokens = tokenize(user_input)
            if not tokens:
                continue
            if tokens == ["exit"]:
                break
            if tokens == ["help"]:
                print_help()
                continue
            execute(metadata, tokens)
        except ValueError:
            print(f"Некорректное значение: {user_input}. Попробуйте снова.")
        print()
