from .standardConceptImplementation import CodedConceptClass, getConceptClass, hasConceptClass
from ..conceptLogic.conceptLogic import Concept, semanticConnectionsNotSufficient, semanticConnectionsNotValid
from .basicDataConcepts import uuidIdentity, NumberConcept, UUIDConcept, identityNamespace
from .basicConstructedConcepts import readDistinctConnection, writeDistinctConnection, ConnectionsConcept
from .standardTools import ensureConcept
import uuid

abstractIdentities = identityNamespace("abstractIdentities")

isDirectAbstractionOf = abstractIdentities("isDirectAbstractionOf")
class DirectAbstraction(metaclass=CodedConceptClass):
    """
    A concept representing a abstract verion of an other concept.
    It has this other concept as conceptContent.
    """
    def getContentFromConnections(semanticConnections, conceptLogic):
        original = readDistinctConnection(isDirectAbstractionOf, semanticConnections, conceptLogic)
        return original
    
    def getConnectionsFromContent(content, conceptLogic):
        return writeDistinctConnection(content, isDirectAbstractionOf, conceptLogic)

    def contentValid(content, conceptLogic):
        return isinstance(content, Concept)
    

constructedAbstractionHasConnections = abstractIdentities("constructedAbstractionHasConnections")
class ConstructedAbstraction(metaclass=CodedConceptClass):
    """
    A concept, that is a distinct construction made of other abstractConcepts
    It has a semanticConnections frozenset as conceptContent that only containes abstractConcepts.
    It uses connectionsConcepts to load and safe its content as semanticConnections
    """
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

referencedAbstractionHasConnections = abstractIdentities("referencedAbstractionHasConnections")
referencedAbstractionHasUUID = abstractIdentities("referencedAbstractionHasUUID")
class ReferencedAbstraction(metaclass=CodedConceptClass):
    """
    A concept, that is defined by its reference uuid and optionally some semantic connections, that can be incomplete.
    It has tuple containing of a uuid and a semanticConnections frozenset as conceptContent
    the frozenset has to contain only abstractConcepts.
    It uses connectionsConcepts to load and safe its content as semanticConnections
    """
    def getContentFromConnections(semanticConnections, conceptLogic):
        connections = readDistinctConnection(referencedAbstractionHasConnections, semanticConnections, conceptLogic)
        if not hasConceptClass(connections, ConnectionsConcept):
            raise semanticConnectionsNotValid()
        uuid = readDistinctConnection(referencedAbstractionHasUUID, semanticConnections, conceptLogic)
        if not hasConceptClass(uuid, UUIDConcept):
            raise semanticConnectionsNotValid()
        return (uuid.content, connections.content)  
    
    def getConnectionsFromContent(content, conceptLogic):
        connections =  writeDistinctConnection(ConnectionsConcept(content[1], conceptLogic), referencedAbstractionHasConnections, conceptLogic)
        return writeDistinctConnection(UUIDConcept(content[0], conceptLogic), referencedAbstractionHasUUID, conceptLogic, connections)
    
    def contentValid(content, conceptLogic):
        if not isinstance(content, tuple) or len(content) != 2:
            return False
        if not type(content[0]) == uuid.UUID:
            return False
        return isinstance(content[1], frozenset) and all([isinstance(connection, tuple) and len(connection) == 3 and all([concept == None or isAbstractConcept(concept) for concept in connection]) for connection in content[1]])
    
    def getContentFromPythonObject(pythonObject, conceptLogic):
        if isinstance(pythonObject, tuple) and len(pythonObject) == 2:
            uuid, connections = pythonObject
        else:
            uuid = pythonObject
            connections = frozenset()
        return (uuid, frozenset([(*[None if y == None else ensureAbstraction(y, conceptLogic) for y in x],) for x in connections]))
    
class ReferencefAbstractionNamespace:
    def __init__(self, name, conceptLogic = None):
        self.name = name
        self.uuid = uuid.uuid3(uuid.NAMESPACE_DNS, name)
        self.conceptLogic = conceptLogic
    def __call__(self, name, connections = []):
        return ReferencedAbstraction((uuid.uuid3(self.uuid, name), connections), self.conceptLogic)

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