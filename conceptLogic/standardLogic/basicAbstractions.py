from .standardConceptImplementation import CodedConceptClass, getConceptClass, hasConceptClass, basicsPrefix
from ..conceptLogic.conceptLogic import Concept, semanticConnectionsNotSufficient, semanticConnectionsNotValid
from .basicDataConcepts import NumberConcept, newIdentityConcept, IdentityConcept
from .basicConstructedConcepts import readDistinctConnection, writeDistinctConnection, ConnectionsConcept, SemanticTripleConcept
from .standardTools import ensureConcept
import uuid

isDirectAbstractionOf = newIdentityConcept("isDirectAbstractionOf", basicsPrefix)
class DirectAbstraction(metaclass=CodedConceptClass):
    """
    A concept representing a abstract verion of an other concept.
    It has this other concept as conceptContent.
    """
    prefix = basicsPrefix
    def getContentFromConnections(semanticConnections, conceptLogic):
        original = readDistinctConnection(isDirectAbstractionOf, semanticConnections, conceptLogic)
        return original
    
    def getConnectionsFromContent(content, conceptLogic):
        return writeDistinctConnection(content, isDirectAbstractionOf, conceptLogic)

    def contentValid(content, conceptLogic):
        return isinstance(content, Concept)
    

constructedAbstractionHasConnections = newIdentityConcept("constructedAbstractionHasConnections", basicsPrefix)
class ConstructedAbstraction(metaclass=CodedConceptClass):
    """
    A concept, that is a distinct construction made of other abstractConcepts
    It has a semanticConnections frozenset as conceptContent that only containes abstractConcepts.
    It uses connectionsConcepts to load and safe its content as semanticConnections
    """
    prefix = basicsPrefix
    def getContentFromConnections(semanticConnections, conceptLogic):
        connections = readDistinctConnection(constructedAbstractionHasConnections, semanticConnections, conceptLogic)
        if not hasConceptClass(connections, ConnectionsConcept):
            raise semanticConnectionsNotValid()
        return connections.content
    
    def getConnectionsFromContent(content, conceptLogic):
        return writeDistinctConnection(ConnectionsConcept(content, conceptLogic), constructedAbstractionHasConnections, conceptLogic)
    
    def contentValid(content, conceptLogic):
        return isinstance(content, frozenset) and all([isinstance(connection, tuple) and len(connection) == 3 and all([concept == None or isAbstractConcept(concept) for concept in connection]) for connection in content])
    
    def getContentFromPythonObject(pythonObject, conceptLogic):
        return frozenset([(*[None if y == None else ensureAbstraction(y, conceptLogic) for y in x],) for x in pythonObject])

referencedAbstractionHasConnections = newIdentityConcept("referencedAbstractionHasConnections", basicsPrefix)
referencedAbstractionHasId = newIdentityConcept("referencedAbstractionHasId", basicsPrefix)
class ReferencedAbstraction(metaclass=CodedConceptClass):
    """
    A concept, that is defined by its reference uuid and optionally some semantic connections, that can be incomplete.
    It has tuple containing of a uuid and a semanticConnections frozenset as conceptContent
    the frozenset has to contain only abstractConcepts.
    It uses connectionsConcepts to load and safe its content as semanticConnections
    """
    prefix = basicsPrefix
    def getContentFromConnections(semanticConnections, conceptLogic):
        connections = readDistinctConnection(referencedAbstractionHasConnections, semanticConnections, conceptLogic)
        if not hasConceptClass(connections, ConnectionsConcept):
            raise semanticConnectionsNotValid()
        id = readDistinctConnection(referencedAbstractionHasId, semanticConnections, conceptLogic)
        if not hasConceptClass(id, IdentityConcept):
            raise semanticConnectionsNotValid()
        return (id.content, connections.content)  
    
    def getConnectionsFromContent(content, conceptLogic):
        connections =  writeDistinctConnection(ConnectionsConcept(content[1], conceptLogic), referencedAbstractionHasConnections, conceptLogic)
        return writeDistinctConnection(IdentityConcept(content[0], conceptLogic), referencedAbstractionHasId, conceptLogic, connections)
    
    def contentValid(content, conceptLogic):
        if not isinstance(content, tuple) or len(content) != 2:
            return False
        if not isinstance(content[0], bytes):
            return False
        return isinstance(content[1], frozenset) and all([isinstance(connection, tuple) and len(connection) == 3 and all([concept == None or isAbstractConcept(concept) for concept in connection]) for connection in content[1]])
    
    def getContentFromPythonObject(pythonObject, conceptLogic):
        if isinstance(pythonObject, tuple) and len(pythonObject) == 2:
            id, connections = pythonObject
        else:
            id = pythonObject
            connections = frozenset()
        return (id, frozenset([(*[None if y == None else ensureAbstraction(y, conceptLogic) for y in x],) for x in connections]))
    
assertsTripleTrue = newIdentityConcept("assertsTripleTrue", basicsPrefix)
class TripleTrueAssertion(metaclass=CodedConceptClass):
    """
    A concept that asserts that a given semanticTriple is true.
    It has a semanticTriple as conceptContent that consists of three abstractConcepts.
    """
    prefix = basicsPrefix
    def getContentFromConnections(semanticConnections, conceptLogic):
        tripleConcept = readDistinctConnection(assertsTripleTrue, semanticConnections, conceptLogic)
        return tripleConcept.content
    
    def getConnectionsFromContent(content, conceptLogic):
        tripleConcept = SemanticTripleConcept(content, conceptLogic)
        return writeDistinctConnection(tripleConcept, assertsTripleTrue, conceptLogic)
    
    def contentValid(content, conceptLogic):
        return isinstance(content, tuple) and len(content) == 3 and all([isAbstractConcept(concept) for concept in content])
    
    def getContentFromPythonObject(pythonObject, conceptLogic):
        return (*[ensureAbstraction(y, conceptLogic) for y in pythonObject],)

def isAbstractConcept(concept):
    if not isinstance(concept, Concept):
        return False
    # TODO This is a temporary solution. Change when GeneralConstructedConcepts with interfaces are done properly
    return getConceptClass(concept).identity in {ConstructedAbstraction, DirectAbstraction, ReferencedAbstraction}

def ensureAbstraction(concept, conceptLogic):
    concept = ensureConcept(concept, conceptLogic)
    if not isAbstractConcept(concept):
        return DirectAbstraction(concept, conceptLogic)
    return concept