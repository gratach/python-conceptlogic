from ..conceptLogic.conceptLogic import Concept, ConceptIdentity


# MixedConceptReference
"""
    A MixedConceptReference in the context of a ConceptLogic is one of the following objects:
        a ConceptIdentity
        a ConceptGetter
        a Concept of the ConceptLogic
    """

class ConceptGetter:
    """
    Base class for a class that can get a concept from a ConceptLogic.
    """
    def getConcept(self, conceptLogic):
        raise NotImplementedError()
    
class SimpleConceptGetter(ConceptGetter):
    """
    A StandardImplementationConceptGetter is a ConceptGetter that uses a StandardConceptImplementation of a parent concept to create the child concept for a given conceptLogic.
    """
    def __init__(self, conceptCreationFunction):
        self.conceptCreationFunction = conceptCreationFunction

    def getConcept(self, conceptLogic):
        return self.conceptCreationFunction(conceptLogic)
    
def emptyConceptIdentity():
    return object.__new__(ConceptIdentity)

class SimpleConceptIdentity(ConceptIdentity):
    def __new__(cls, *args, seedObject = None):
        if seedObject != None:
            assert isinstance(seedObject, ConceptIdentity)
            seedObject.__class__ = SimpleConceptIdentity
            return seedObject
        return object.__new__(cls)
    def __init__(self, conceptImplementation, content, name, seedObject = None):
        self.identityName = name
        self.content = content
        super().__init__(conceptImplementation, lambda conceptLogic : content)
    def getConcept(self, conceptLogic):
        return conceptLogic.getRawConceptFromIdentity(self)
    
def ensureConcept(mixedConceptReference, conceptLogic):
    """
    This function takes a MixedConceptReference and a conceptLogic and returns a concept.
    """
    if type(mixedConceptReference) == Concept:
        if not mixedConceptReference.conceptLogic == conceptLogic:
            raise Exception("The conceptLogic of the concept does not match the given conceptLogic.")
        return mixedConceptReference
    if isinstance(mixedConceptReference, ConceptGetter):
        return mixedConceptReference.getConcept(conceptLogic)
    if isinstance(mixedConceptReference, ConceptIdentity):
        return conceptLogic.getRawConceptFromIdentity(mixedConceptReference)
    raise Exception("The given mixedConceptReference is not a ConceptIdentity, a ConceptGetter or a Concept.")