"""Constants shared by modules of the database."""

# Files: table metadata and the folder with the records of every table.
META_FILE = "db_meta.json"
DATA_DIR = "data"
JSON_INDENT = 4  # spaces of indentation in the saved JSON files

# Table schema: the automatic key column and the allowed column types.
ID_COLUMN = "ID"
VALID_TYPES = {"int": int, "str": str, "bool": bool}

# Command loop: the input prompt and the names of all known commands.
PROMPT = ">>>Введите команду: "
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
