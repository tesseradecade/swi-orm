from prolog import Prolog, QuerySet
import os

prolog = Prolog(path_to_swipl=os.environ["path_to_swipl"])


@prolog.predicate
def person(name: str, age: int):
    yield name, age


@prolog.predicate
def old(name: str):
    x = prolog.query_var("Y")
    y = prolog.query_var("Y")
    return person(name, x) and y > 60


prolog << person("andrew", 12)
prolog << person("arseny", 15)
prolog << person("vitalii", 73)

prolog.load_predicates()

X = prolog.query_var("X")
Y = prolog.query_var("Y")

q = prolog >> person(X, Y)

print(q.fetch())  # generator object
print(q.fetchone())  # {"x": "andrew", "y": 12}

# ({"x": "andrew", "y": 12}, {"x": "arseny", "y": 15}, {"x": "vitalii", "y": 16})
print(q.fetchall())

q = QuerySet(old("vitalii"), session=prolog)

print(q.prove())  # True
prolog.halt()
