# Python2prolog

Python object oriented prolog translator. Project is being tested and doesnt implement lots of main features.

### Installation

Install [swipy](https://github.com/timoniq/swipy) (fork of [AILab-FOI/pyxf](https://github.com/AILab-FOI/pyxf)) and `pexpect` requirements:

```shell script
pip install pexpect git+https://github.com/timoniq/swipy
```

Clone the repository:

```shell script
git clone https://github.com/tesseradecade/prolog.git
```

Go to the repository folder and install with `setup.py`:

```shell script
cd prolog
python setup.py install
```

### Usage

Use main instance of Prolog as a container for predicates. 

`Lshift` (`<<`) operator for prolog instance adds a new predicate with `assert/1` 

`Rshift` (`>>`) operator for prolog instance makes a query

```python
from prolog import Prolog
from prolog import QueryVar

prolog = Prolog("/path/to/prolog")
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
