import typing
import types
import ast

from inspect import getsource, isclass
from prolog.predicate import predicate, DEFINITIONS, Qvs
from prolog.query import QueryVar, QuerySet
from prolog.swipl import Swipl

PREDICATE_ONE_DEP = "{0}({2}) :- {1}({3})."
CONSTS: Qvs = {"_": QueryVar("_")}


class Prolog(Swipl):
    def __init__(
        self,
        path_to_swipl: str,
        args: typing.Optional[typing.List[str]] = None,
        predicates: typing.Optional[typing.List[str]] = None,
    ):
        super().__init__(path_to_swipl, args)
        self.predicates = predicates or []

    def predicate(
        self,
        func: typing.Optional[types.FunctionType] = None,
        source: typing.Optional[str] = None,
        source_sub: typing.Optional[typing.Callable[[str], str]] = None,
        spec_parser: typing.Optional[
            typing.Callable[[list, str, typing.Callable, list], str]
        ] = None,
    ):
        """ Assign free predicate with decorator / with source
        :param func: wrapped function
        :param source:
        :param source_sub:
        :param spec_parser:
        """
        if isclass(func):
            format_args = ", ".join("{}" for _ in func.__annotations__)
            query_set = predicate(
                f"{func.__name__.lower()}({format_args})."
            )  # TODO: type checks
            func.__str__ = lambda s: query_set(
                *(getattr(s, n) for n in func.__annotations__)
            )
            return func

        if not source:
            source = getsource(func)

        if source_sub:
            source = source_sub(source)

        code = ast.parse(source).body[0]
        qvs: Qvs = {}
        args = [a.arg.upper() for a in code.args.args]

        for a in code.args.args:
            qvs[a.arg] = a.arg.upper()

        for e in code.body:
            if e.__class__ is ast.Assign:
                if e.value.__class__ is not ast.Call:
                    raise RuntimeError("Only query var get allowed")
                local_name, prolog_name = e.targets[0].id, e.value.args[0].s
                qvs[local_name] = prolog_name

        if spec_parser is not None:
            result = spec_parser(code.body, source, func, args)
            self << result
            return result

        elif code.body[-1].__class__ is ast.Expr:
            return self.expr_caster(code.body[-1], func, qvs)

        elif code.body[-1].__class__ is ast.Return:
            return self.return_caster(code.body[-1], func, qvs, args)

        raise RuntimeError("Undefined return or yield expression")

    def load_predicates(self) -> None:
        """ Loads assigned predicates to the local swi-prolog session """
        self.load_lines(self.predicates)

    @staticmethod
    def query_var(prolog_name: str) -> QueryVar:
        prolog_name = prolog_name.capitalize()
        return QueryVar(prolog_name)

    @staticmethod
    def to_qv(value: typing.Any) -> QueryVar:
        return QueryVar(repr(value))

    @staticmethod
    def query_vars(*prolog_name: str) -> typing.Tuple[QueryVar, ...]:
        # TODO: maybe generics
        return tuple(map(QueryVar, prolog_name))

    def __lshift__(self, pred: str):
        """ Add predicate using lshift """
        self.predicates.append(str(pred))

    def __rshift__(self, query: str) -> QuerySet[dict]:
        """ Making a query using rshift """
        return QuerySet(str(query), session=self)

    def expr_caster(self, body: ast.Expr, func: typing.Callable, qvs: Qvs):
        """ Caster for storing predicates (p/1) """
        expr = body.value
        if expr.__class__ is ast.Yield:
            format_args = ", ".join("{}" for _ in qvs.values())
            return predicate(f"{func.__name__.lower()}({format_args}).")

    def return_caster(
        self, body: ast.Return, func: typing.Callable, qvs: Qvs, args: typing.List[str]
    ):
        """ Caster for conditionals """
        expr = body.value

        if getattr(expr, "func", 0):

            return self << PREDICATE_ONE_DEP.format(
                func.__name__.lower(),
                expr.func.id.lower(),
                ", ".join(args),
                ", ".join(qvs[a.id] for a in expr.args),
            )

        elif getattr(expr, "s", 0):
            return (
                self
                << f"{func.__name__.lower()}({', '.join(qvs.values())}) :- {expr.s}"
            )

        elif getattr(expr, "op", 0):
            list_op = [expr.values[0], expr.op, *expr.values[1:]]

            while list_op[0].__class__ is ast.BoolOp:
                op = list_op[0]
                list_op.pop(0)
                list_op = [op.values[0], op.op, *op.values[1:], *list_op]

            clause = f"{func.__name__.lower()}({', '.join(args)}) :- "
            operator = ", "

            for node in list_op:
                if node.__class__ is ast.Call:
                    clause += f"{node.func.id.lower()}({', '.join(qvs[a.id] for a in node.args)})"
                elif node.__class__ is ast.And:
                    operator = ", "
                    continue
                elif node.__class__ is ast.Or:
                    operator = "; "
                    continue
                elif node.__class__ is ast.Compare:
                    left = self.prolog_definition(node.left, qvs)
                    right = self.prolog_definition(node.comparators[0], qvs)
                    op = self.operator_caster(node.ops[0])
                    clause += f"{left} {op} {right}"
                else:
                    clause += self.operator_caster(node)

                clause += operator
            clause = clause[:-2]
            clause += "."
            self << clause

            format_args = ", ".join("{}" for _ in args)
            return predicate(f"{func.__name__.lower()}({format_args}).")

    def operator_caster(self, body: ast.operator):
        """ Caster for operators """
        operators = {
            ast.Add: "+",
            ast.Sub: "-",
            ast.Eq: "=",
            ast.NotEq: "\\=",
            ast.And: ", ",
            ast.Or: "; ",
            ast.Gt: ">",
            ast.Lt: "<",
        }

        if body.__class__ is ast.BoolOp:
            return self.operator_caster(body.op).join(
                self.prolog_definition(value, []) for value in body.values
            )
        elif body.__class__ is ast.Str:
            return body.s

        if body.__class__ not in operators:
            raise RuntimeError(body.__class__.__name__ + " operator is not assigned")
        return operators[body.__class__]

    @staticmethod
    def prolog_definition(node: typing.Any, qvs: Qvs):
        """ Find a definition """
        return DEFINITIONS.get(node.__class__)(node, qvs)
