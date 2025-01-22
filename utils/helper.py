import string


def remove_punc(text):
    exclude = set(string.punctuation)
    return ''.join(ch for ch in text if ch not in exclude)


def replace_space_with_underscope(text: str):
    space = " "
    underscore = "\_"
    return text.replace(space, underscore)


def normalize_text(text: str):
    return replace_space_with_underscope(remove_punc(text))
