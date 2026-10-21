import shlex


def tokenize(text):
    """Split a command into tokens: quoted strings keep their quotes."""
    lexer = shlex.shlex(text, posix=False, punctuation_chars="=,()")
    lexer.whitespace_split = True
    return list(lexer)


def parse_value(token):
    """Convert a token into str (in quotes), bool (true/false) or int."""
    if len(token) >= 2 and token[0] == token[-1] and token[0] in ("'", '"'):
        return token[1:-1]
    if token.lower() in ("true", "false"):
        return token.lower() == "true"
    try:
        return int(token)
    except ValueError:
        raise ValueError(token) from None


def split_items(tokens):
    """Split tokens into groups separated by commas."""
    items = [[]]
    for token in tokens:
        if token == ",":
            items.append([])
        else:
            items[-1].append(token)
    return items


def parse_values(tokens):
    """Turn the tokens of ("Sergei", 28, true) into ["Sergei", 28, True]."""
    if len(tokens) < 2 or tokens[0] != "(" or tokens[-1] != ")":
        raise ValueError
    values = []
    for item in split_items(tokens[1:-1]):
        if len(item) != 1:
            raise ValueError
        values.append(parse_value(item[0]))
    return values


def parse_condition(tokens):
    """Turn the tokens of age = 28 into {"age": 28}."""
    if len(tokens) != 3 or tokens[1] != "=":
        raise ValueError
    return {tokens[0]: parse_value(tokens[2])}


def parse_set(tokens):
    """Turn the tokens of age = 29, name = "Bob" into {"age": 29, "name": "Bob"}."""
    clause = {}
    for item in split_items(tokens):
        clause.update(parse_condition(item))
    return clause


def split_where(tokens):
    """Split tokens at the where keyword into parts before and after it."""
    if "where" not in tokens:
        raise ValueError
    position = tokens.index("where")
    return tokens[:position], tokens[position + 1 :]
