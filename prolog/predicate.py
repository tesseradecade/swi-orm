import ast


def predicate(predicate_pattern: str):
    """ Translate a predicate """

    def format_predicate(*args):
        args = [
            repr(a).replace("'", '"') if not isinstance(a, QueryVar) else a.name
            for a in args
        ]
        return predicate_pattern.format(*args)

    return format_predicate


class ASTDefinitions:
    @staticmethod
    def str_definition(node: ast.Str):
        return repr(node.s).replace("'", '"')

    @staticmethod
    def num_definition(node: ast.Num):
        return str(node.n)

    @staticmethod
    def name_definition(node: ast.Name):
        return str(node.id).upper()

    @staticmethod
    def call_definition(node: ast.Call):
        return f"{node.func.id}({', '.join(DEFINITIONS[a.__class__](a) for a in node.args)})"


class QueryVar:
    def __init__(self, query_var: str):
        self.name = query_var

    def __str__(self):
        return self.name


DEFINITIONS = {
    ast.Str: ASTDefinitions.str_definition,
    ast.Num: ASTDefinitions.num_definition,
    ast.Name: ASTDefinitions.name_definition,
    ast.Call: ASTDefinitions.call_definition,
}
