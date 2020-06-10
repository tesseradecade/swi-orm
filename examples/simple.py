from prolog import Prolog, QueryVar

prolog = Prolog(path_to_swipl="/opt/local/lib/swipl/bin/x86_64-darwin/swipl")
X = QueryVar("X")


@prolog.predicate
def person(name: str, age: int):
    yield


@prolog.predicate
def old(name: str):
    return person(name, X) and X > 40


prolog << person("ars", 15)
prolog << person("vas", 17)
prolog << person("and", 50)

prolog.load_predicates()
query = prolog >> old("and")

print(query)
