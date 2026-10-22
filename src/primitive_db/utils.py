import json
import os

DATA_DIR = "data"


def load_metadata(filepath):
    """Load database metadata from a JSON file; return {} if it does not exist."""
    try:
        with open(filepath, encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}


def save_metadata(filepath, data):
    """Save database metadata to a JSON file."""
    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def table_path(table_name):
    """Return the path of the JSON file with the records of a table."""
    return os.path.join(DATA_DIR, f"{table_name}.json")


def load_table_data(table_name):
    """Load the records of a table; return [] if the table has no data file."""
    try:
        with open(table_path(table_name), encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return []


def save_table_data(table_name, data):
    """Save the records of a table, creating the data directory if needed."""
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(table_path(table_name), "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def delete_table_data(table_name):
    """Delete the data file of a table, if it exists."""
    try:
        os.remove(table_path(table_name))
    except FileNotFoundError:
        pass
