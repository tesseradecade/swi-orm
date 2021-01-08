import ast
from typing import Dict
from .query import normalize_value

Qvs = Dict[str, str]


def predicate(predicate_pattern: str):
    """ Translate a predicate """

    def format_predicate(*args):
        args = [normalize_value(a).replace("'", '"') for a in args]
        return predicate_pattern.format(*args)

    return format_predicate


class ASTDefinitions:
    @staticmethod
    def str_definition(node: ast.Str, _):
        return repr(node.s).replace("'", '"')

    @staticmethod
    def num_definition(node: ast.Num, _):
        return str(node.n)

    @staticmethod
    def name_definition(node: ast.Name, qvs: Qvs):
        return qvs[node.id]

    @staticmethod
    def call_definition(node: ast.Call, _):
        return f"{node.func.id}({', '.join(DEFINITIONS[a.__class__](a) for a in node.args)})"


DEFINITIONS = {
    ast.Str: ASTDefinitions.str_definition,
    ast.Num: ASTDefinitions.num_definition,
    ast.Name: ASTDefinitions.name_definition,
    ast.Call: ASTDefinitions.call_definition,
}
