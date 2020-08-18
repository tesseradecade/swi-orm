# Python2prolog :lips:

Python object oriented prolog translator. Project is being actively tested.

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

`Rshift` (`>>`) operator for prolog instance makes a query

```python
from prolog import Prolog
from prolog import QueryVar

prolog = Prolog("/path/to/prolog") # For example for me is "/opt/local/lib/swipl/bin/x86_64-darwin/swipl"
X = QueryVar("X")

# You can make objective predicates
@prolog.predicate
def human(name: str, age: int):
    yield name, age # Use yield to assign storing type to the predicate

@prolog.predicate
def old(name: str):
    return human(name, X) and X > 60

prolog << human("Ivan", 73)  # You can simply pass objective predicate
prolog << 'human("Masha", 15).'  # Or string clause can be passed

# Load predicates to the prolog session created on instance of Prolog init
prolog.load_predicates()

print(prolog >> old("Ivan"))  # true
```

## Documentation

Documentation is not planned by me still but you can feel free to contribute

Leave a :star: if this project helped you  
Made with :heart: by [timoniq](https://github.com/timoniq)
