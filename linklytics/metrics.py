def count_words(text: str) -> int:
    return len(text.split())


def count_lines(text: str) -> int:
    return len(text.split("\n"))


def get_hook(text: str) -> str:
    for line in text.split("\n"):
        if line != "":
            return line
    return "ERROR: No hook found"
