from prolog import Prolog

prolog = Prolog(path_to_swipl="/opt/local/lib/swipl/bin/x86_64-darwin/swipl")

@prolog.predicate
def man(x):
    yield

@prolog.predicate
def female(x):
    yield

@prolog.predicate
def loves(a, b):
    return man(a) and female(b)


prolog << man("arsenii")
prolog << man("kesha1225")
prolog << man("chel")

prolog << female("crinny")
prolog << female("kotiq")
prolog << female("linker")

prolog.load_predicates()
query = prolog >> 'loves(X, Y).'

print("\n".join(prolog.predicates))
print(query)
