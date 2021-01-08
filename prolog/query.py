from typing import (
    Any,
    Dict,
    Iterator,
    Union,
    Type,
    Tuple,
    Optional,
    Generic,
    NoReturn,
    TypeVar,
    TYPE_CHECKING,
)

if TYPE_CHECKING:
    from prolog.prolog import Prolog

QS_Foreign = Union[str, "QuerySet"]
T = TypeVar("T")


def normalize_value(v: Any):
    if isinstance(v, QueryVar):
        return v
    elif isinstance(v, (list, tuple)):
        return "[" + ", ".join(str(normalize_value(vv)) for vv in v) + "]"
    return repr(v)


class QueryError(Exception):
    pass


class QueryVar(str):
    def __init__(self, _):
        super().__init__()
        self.incomplete = False

    def __or__(self, other: Any) -> "QueryVar":
        qv = QueryVar((self + "|" + other).replace("'", '"'))
        qv.incomplete = True
        return qv


class QuerySet(Generic[T]):
    def __init__(
        self,
        prolog: str,
        pre_set: Optional[Dict[str, Any]] = None,
        dataclass: Type[T] = dict,
        session: Optional["Prolog"] = None,
    ):
        self.prolog = prolog if not prolog.endswith(".") else prolog[:-1]
        self.pre_set = pre_set or {}
        self.dataclass = dataclass
        self.session = session

    def __imul__(self, qs: QS_Foreign) -> NoReturn:
        self.prolog = self.__mul__(qs)

    def __mul__(self, qs: QS_Foreign) -> "QuerySet":
        return QuerySet(self.prolog + ", " + str(qs))

    def __iadd__(self, qs: QS_Foreign) -> NoReturn:
        self.prolog = self.__add__(qs).prolog

    def __add__(self, qs: QS_Foreign) -> "QuerySet":
        return QuerySet(self.prolog + "; " + str(qs))

    def __str__(self) -> str:
        return self.prolog

    def fetch(
        self, session: Optional["Prolog"] = None, only_prove: bool = False
    ) -> Iterator[Union[T, bool]]:
        session = session or self.session
        assert session, "Session must be set"

        for data in session.query(self.expression):
            if isinstance(data, bool):
                if not only_prove:
                    raise QueryError(f"Query returned proof {self.prolog!r}")
                yield data
            data.update(self.pre_set)
            yield self.dataclass(**data)

    def fetchall(self, session: Optional["Prolog"] = None) -> Tuple[T, ...]:
        return tuple(self.fetch(session))

    def fetchone(self, session: Optional["Prolog"] = None) -> T:
        for data in self.fetch(session):
            (session or self.session).send_dot()
            return data

    def prove(self, session: Optional["Prolog"] = None) -> bool:
        for data in self.fetch(session, only_prove=True):
            (session or self.session).send_dot()
            return data

    @property
    def expression(self) -> str:
        return str(self.prolog) + "."
