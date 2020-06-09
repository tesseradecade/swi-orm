def predicate(predicate_pattern: str):
    """ Translate a predicate """
    def format_predicate(*args):
        args = [repr(a).replace("'", '"') for a in args]
        return predicate_pattern.format(*args)
    return format_predicate
