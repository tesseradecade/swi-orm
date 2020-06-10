from prolog import Prolog, QueryVar

prolog = Prolog(path_to_swipl="/opt/local/lib/swipl/bin/x86_64-darwin/swipl")
X = QueryVar("X")

@prolog.predicate
def person(name: str, age: int):
    yield name, age

@prolog.predicate
def old(name: str):
    return person(name, X) and X > 60


prolog << person("arsenii", 15)
prolog << person("vitali", 17)
prolog << person("crinny", 73)

prolog.load_predicates()
query = prolog >> old("crinny")

print(query)  # true
