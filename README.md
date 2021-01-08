# Prolog Quering and (partially) ORM for python

Prolog translator, query builder, ORM

## Installation

### Install swi-prolog

Install [last stable version of SWI-Prolog here](https://www.swi-prolog.org/download/stable)

### Install this translator

With pip:

```shell script
pip install prolog-interface
```

With poetry:

```shell script
poetry add prolog-interface
```

## Usage

Use main instance of Prolog as a container for predicates. 

`Lshift` (`<<`) operator for prolog instance adds a new predicate with `assert/1`  
Predicates in Lshift art just added to the simple container, to load them to prolog after filling it use `.load_predicates()` 

`Rshift` (`>>`) operator for prolog instance makes a query (`QuerySet`), or you can simply use `QuerySet` with instance of `Prolog`


### [low-level querying example](./examples/querying.py)

```python
from prolog import Prolog

prolog = Prolog("/path/to/prolog") # For example for me is "/opt/local/lib/swipl/bin/x86_64-darwin/swipl"

# Constant predicates declaration
@prolog.predicate
def person(name: str, age: int):
    yield name, age

# Consequential predicates declaration
@prolog.predicate
def old(name: str):
    x = prolog.query_var("X")
    return person(name, x) and x > 60


# Declaration of facts
prolog << person("Gomez", 52)
prolog << person("Morticia", 48)
prolog << person("Pugsley", 13)
prolog << person("Wednesday", 13)
prolog << person("Grandmama", 100)

prolog.load_predicates() # Loading predicates to current prolog session

# Query vars for syntax compatibility
X = prolog.query_var("X")
Y = prolog.query_var("Y")

# Making a query set
q = prolog >> person(X, Y)

print(q.fetch())  # generator object
print(q.fetchone())  # {"x": "andrew", "y": 12}

# ({"x": "Gomez", "y": 52}, {"x": "Morticia", "y": 48}, ...)
print(q.fetchall())

q = prolog >> old("Grandmama") # or QuerySet(old("Grandmama"), session=prolog)

print(q.prove())  # True
prolog.halt()
```

### [orm example](./examples/orm.py)

```python
from prolog import Prolog, ANONYMOUS_QV as _, Predicate
from dataclasses import dataclass
from typing import List

prolog = Prolog(path_to_swipl="/path/to/prolog")


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

q = Person.filter(children=[_|_])

for person in q.fetch(prolog):
    print(person.name, "has children")

prolog.halt()
```

## Documentation

Later maybe, feel free to contribute

Leave a :star: if this project helped you  
Made with :heart: by [timoniq](https://github.com/timoniq)
