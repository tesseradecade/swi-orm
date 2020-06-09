import typing
import ast
import json

from swipy import Swipl
from inspect import getsource
from .predicate import predicate

PREDICATE_ONE_DEP = "{0}({2}) :- {1}({3})."

def json_parser(value: str, keys):
    """ Parse multiple responses """
    value = value.replace("...", "null").replace("|", ", ")
    return json.loads(value)


class Prolog(Swipl):
    predicates: typing.List[str] = []

    def predicate(self, func: typing.Callable):
        """ Assign free predicate with decorator
        :param func: wrapped function
        """
        source = getsource(func)
        code = ast.parse(source).body[0]
        args = [a.arg.upper() for a in code.args.args]

        if code.body[0].__class__ is ast.Expr:
            return self.expr_caster(code.body[0], func, args)

        elif code.body[0].__class__ is ast.Return:
            return self.return_caster(code.body[0], func, args)

        return func

    def load_predicates(self) -> None:
        """ Loads assigned predicates to the local swi-prolog session """
        self.load_lines(self.predicates)

    def __lshift__(self, pred: str):
        """ Add predicate using lshift """
        self.predicates.append(pred)

    def __rshift__(self, query: str):
        """ Making a query using rshift """
        self.response_parser = json_parser
        return self.query(query)

    def expr_caster(self, body: ast.Expr, func: typing.Callable, args: typing.Iterable):
        """ Caster for storing predicates (p/1) """
        expr = body.value
        if expr.__class__ is ast.Yield:
            format_args = ", ".join('{}' for _ in args)
            return predicate(f"{func.__name__}({format_args}).")

    def return_caster(self, body: ast.Return, func: typing.Callable, args: typing.Iterable):
        """ Caster for conditionals """
        expr = body.value

        if getattr(expr, "func", 0):
            return self << PREDICATE_ONE_DEP.format(
                func.__name__,
                expr.func.id,
                ', '.join(args),
                ', '.join(a.id.upper() for a in expr.args),
            )

        elif getattr(expr, "op", 0):
            list_op = [expr.values[0], expr.op, *expr.values[1:]]

            while list_op[0].__class__ is ast.BoolOp:
                op = list_op[0]
                list_op.pop(0)
                list_op = [op.values[0], op.op, *op.values[1:], *list_op]

            clause = f"{func.__name__}({', '.join(args)}) :- "

            for node in list_op:
                if node.__class__ is ast.Call:
                    clause += f"{node.func.id}({', '.join(a.id.upper() for a in node.args)})"
                elif node.__class__ is ast.And:
                    clause += ", "
                elif node.__class__ is ast.Or:
                    clause += "; "

            clause += "."
            self << clause