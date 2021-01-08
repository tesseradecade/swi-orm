def pythonize(value: str) -> str:
    value = value.replace("...", "null").replace("|", ", ")
    return value
