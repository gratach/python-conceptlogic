from io import StringIO
from conceptLogic import *

sl = StandardLogic([NumberConcept, StringConcept])
sl.activate()
concepts = set()
nr = NumberConcept(12, sl)
t1 = StringConcept("hallo world", sl)
t2 = StringConcept("some text with newline \n and \"\'", sl)
s1 = SetConcept(frozenset([nr, t1]), sl)
s2 = SetConcept(frozenset([nr, t2]), sl)
s3 = SetConcept(frozenset([nr, t1]), sl)
da1 = DirectAbstraction(nr, sl)
cc1 = ConnectionConcept((nr, nr, None), sl)
csc1 = ConnectionsConcept([(None, isInstanceOf, nr)], sl)
concepts.update(sl.getLoadedConcepts())


with StringIO() as s:
    writeTriples(concepts, s)
    concepts.update(sl.getLoadedConcepts())
    print(s.getvalue())
    s.seek(0)
    rt1 = readTriples(s, sl)
    s.seek(0)
    rt2 = readTriples(s, sl)
    print(all([c in rt1.values() for c in concepts]))
    for c in concepts.difference(set(rt1.values())):
        print(getConceptName(c))
    print(set(rt1) == set(rt2))
    print(s1 == s3)

#for c in concepts:
#    print(getConceptName(c), getConceptName(getConceptClass(c)))