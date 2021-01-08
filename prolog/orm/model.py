from prolog.query import QueryVar, QuerySet
from prolog.predicate import predicate
from prolog.orm.exceptions import ORMException
from prolog.orm.utils import process_var
from typing import Union

Arg = Union[str, int, list, QueryVar]


class Predicate:
    @classmethod
    def filter(cls, *args: Arg, **kwargs) -> QuerySet:
        # TODO: type checks
        query_args = []
        pre_set = dict()

        format_args = ", ".join("{}" for _ in cls.__annotations__)
        format_predicate = predicate(f"{cls.__name__.lower()}({format_args})")

        for i, required_name in enumerate(cls.__annotations__):
            query_arg = QueryVar(required_name.capitalize())
            if required_name in kwargs:
                query_arg = kwargs[required_name]
                pre_set[required_name] = query_arg
            elif len(args) > i:
                query_arg = args[i]
                pre_set[required_name] = query_arg
            query_args.append(query_arg)

        for k, v in pre_set.items():
            pre_set[k] = process_var(v)

        return QuerySet(format_predicate(*query_args), pre_set=pre_set, dataclass=cls)

    def __str__(self):
        args = ", ".join("{}" for _ in self.__annotations__)
        query_set = predicate(f"{self.__class__.__name__.lower()}({args}).")
        return query_set(*(getattr(self, n) for n in self.__annotations__))
