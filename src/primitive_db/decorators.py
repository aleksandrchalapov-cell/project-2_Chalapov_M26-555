import time


def handle_db_errors(func):
    """Print database errors raised by func instead of crashing: return None."""

    def wrapper(*args, **kwargs):
        """Call func and print the message of a database error if it fails."""
        try:
            return func(*args, **kwargs)
        except FileNotFoundError:
            print(
                "Ошибка: Файл данных не найден. "
                "Возможно, база данных не инициализирована."
            )
        except KeyError as error:
            print(error.args[0])
        except ValueError as error:
            print(error)
        except Exception as error:
            print(f"Произошла непредвиденная ошибка: {error}")
        return None

    return wrapper


def confirm_action(action_name):
    """Ask the user to confirm the action before running the function."""

    def decorator(func):
        """Wrap func with the confirmation question."""

        def wrapper(*args, **kwargs):
            """Ask the question and call func only if the answer is "y"."""
            question = f'Вы уверены, что хотите выполнить "{action_name}"? [y/n]: '
            try:
                answer = input(question)
            except (EOFError, KeyboardInterrupt):
                print()
                answer = ""
            if answer.strip().lower() != "y":
                print("Операция отменена.")
                return None
            return func(*args, **kwargs)

        return wrapper

    return decorator


def log_time(func):
    """Print the time taken by func to run."""

    def wrapper(*args, **kwargs):
        """Call func, print how long it ran and return its result."""
        start = time.monotonic()
        result = func(*args, **kwargs)
        elapsed = time.monotonic() - start
        print(f"Функция {func.__name__} выполнилась за {elapsed:.3f} секунд.")
        return result

    return wrapper


def create_cacher():
    """Return cache_result(key, value_func), which keeps its cache in a closure."""
    cache = {}

    def cache_result(key, value_func):
        """Return the cached value for key, calling value_func only the first time."""
        if key not in cache:
            cache[key] = value_func()
        return cache[key]

    cache_result.clear = cache.clear
    return cache_result
