from primitive_db.utils import load_table_data

VALID_TYPES = {"int": int, "str": str, "bool": bool}


def create_table(metadata, table_name, columns):
    """Add a table with an automatic ID:int column and return the metadata."""
    if not table_name.isidentifier():
        print(f"Некорректное значение: {table_name}. Попробуйте снова.")
        return None
    if table_name in metadata:
        print(f'Ошибка: Таблица "{table_name}" уже существует.')
        return None
    schema = {"ID": "int"}
    for column in columns:
        name, _, column_type = column.partition(":")
        if name == "ID" and column_type == "int":
            continue
        if not name or column_type not in VALID_TYPES or name in schema:
            print(f"Некорректное значение: {column}. Попробуйте снова.")
            return None
        schema[name] = column_type
    metadata[table_name] = schema
    described = ", ".join(f"{name}:{kind}" for name, kind in schema.items())
    print(f'Таблица "{table_name}" успешно создана со столбцами: {described}')
    return metadata


def drop_table(metadata, table_name):
    """Remove a table from the metadata and return the metadata."""
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return None
    del metadata[table_name]
    print(f'Таблица "{table_name}" успешно удалена.')
    return metadata


def list_tables(metadata):
    """Print the names of all tables."""
    if not metadata:
        print("Таблиц пока нет.")
    for table_name in metadata:
        print(f"- {table_name}")


def table_exists(metadata, table_name):
    """Return True if the table exists; otherwise print an error."""
    if table_name in metadata:
        return True
    print(f'Ошибка: Таблица "{table_name}" не существует.')
    return False


def validate_clause(metadata, table_name, clause):
    """Return True if the table has every column and the values fit their types."""
    if not table_exists(metadata, table_name):
        return False
    schema = metadata[table_name]
    for column, value in clause.items():
        if column not in schema:
            print(f'Ошибка: Столбец "{column}" не существует.')
            return False
        if type(value) is not VALID_TYPES[schema[column]]:
            print(f"Некорректное значение: {value!r}. Попробуйте снова.")
            return False
    return True


def insert(metadata, table_name, values):
    """Add a record with an automatic ID and return the table data."""
    if not table_exists(metadata, table_name):
        return None
    columns = [column for column in metadata[table_name] if column != "ID"]
    if len(values) != len(columns):
        print(f"Ошибка: Ожидается значений: {len(columns)}, получено: {len(values)}.")
        return None
    record = dict(zip(columns, values))
    if not validate_clause(metadata, table_name, record):
        return None
    table_data = load_table_data(table_name)
    record_id = max((row["ID"] for row in table_data), default=0) + 1
    table_data.append({"ID": record_id, **record})
    print(f'Запись с ID={record_id} успешно добавлена в таблицу "{table_name}".')
    return table_data


def matches(record, where_clause):
    """Return True if the record has every value of the where clause."""
    return all(record.get(column) == value for column, value in where_clause.items())


def select(table_data, where_clause=None):
    """Return all records, or only the ones that match the where clause."""
    if where_clause is None:
        return table_data
    return [record for record in table_data if matches(record, where_clause)]


def update(table_data, set_clause, where_clause):
    """Apply the set clause to every record that matches the where clause."""
    for record in table_data:
        if matches(record, where_clause):
            record.update(set_clause)
    return table_data


def delete(table_data, where_clause):
    """Remove every record that matches the where clause."""
    return [record for record in table_data if not matches(record, where_clause)]


def table_info(metadata, table_name):
    """Print the columns and the number of records of a table."""
    if not table_exists(metadata, table_name):
        return
    schema = metadata[table_name]
    described = ", ".join(f"{name}:{kind}" for name, kind in schema.items())
    print(f"Таблица: {table_name}")
    print(f"Столбцы: {described}")
    print(f"Количество записей: {len(load_table_data(table_name))}")
