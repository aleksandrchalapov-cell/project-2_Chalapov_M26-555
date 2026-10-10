import prompt
def print_help() -> None:
    """Print the list of available commands."""
    print("<command> exit - выйти из программы")
    print("<command> help - справочная информация")


def welcome() -> None:
    """Greet the user and run the command loop until 'exit'."""
    print("Первая попытка запустить проект!")
    print()
    print("***")
    print_help()
    while True:
        command = prompt.string("Введите команду: ")
        if command == "exit":
            break
        elif command == "help":
            print()
            print_help()
