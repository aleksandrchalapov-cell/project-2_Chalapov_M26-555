VALID_TYPES = ("int", "str", "bool")


def create_table(metadata, table_name, columns):
    """Add a table with an automatic ID:int column and return the metadata."""
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
