from typing import Any
from prolog.query import QueryVar
from prolog.orm.partial_fields import PartialField


def process_var(value: Any) -> Any:
    if isinstance(value, list):
        for v in value:
            if isinstance(v, QueryVar):
                return PartialField(v)
    elif isinstance(value, QueryVar):
        return PartialField(value)
    return value
