from typing import Generic, TypeVar

T = TypeVar("T")


class PartialField(Generic[T]):
    def __init__(self, o: T):
        self.o = o

    def __repr__(self) -> str:
        return f"<PartialField ({self.o})>"
