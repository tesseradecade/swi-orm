from prolog import Prolog, ANONYMOUS_QV as _, Predicate
from dataclasses import dataclass
from typing import List
import os

prolog = Prolog(path_to_swipl=os.environ["path_to_swipl"])


@dataclass
class Person(Predicate):
    name: str
    sex: int
    age: int
    children: List[str]


prolog << Person("Gomez", 0, 52, ["Wednesday", "Pugsley"])
prolog << Person("Morticia", 1, 48, ["Wednesday", "Pugsley"])
prolog << Person("Pugsley", 0, 13, [])
prolog << Person("Wednesday", 1, 13, [])
prolog << Person("Grandmama", 1, 100, ["Gomez"])

prolog.load_predicates()

q = Person.filter(children=[_ | _])

for person in q.fetch(prolog):
    print(person.name, "has children")
