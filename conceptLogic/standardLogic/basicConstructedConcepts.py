
from .standardConceptImplementation import CodedConceptClass, getConceptClass
from ..conceptLogic.conceptLogic import Concept, semanticConnectionsNotSufficient, semanticConnectionsNotValid
from .basicDataConcepts import uuidIdentity, NumberConcept, UUIDConcept, identityNamespace
from .standardTools import ensureConcept

basicIdentities = identityNamespace("basicIdentities")
hasSetCount = basicIdentities("hasSetCount")
hasSetEntry = basicIdentities("hasSetEntry")

def readDistinctConnections(connectionType, expectedNumberOfConnections, semanticConnections, conceptLogic):
    predConcept = ensureConcept(connectionType, conceptLogic)
    collectedResults = [z for x, y, z in semanticConnections if x == None and y == predConcept]
    if len(collectedResults) < expectedNumberOfConnections:
        raise semanticConnectionsNotSufficient()
    if len(collectedResults) > expectedNumberOfConnections:
        raise semanticConnectionsNotValid()
    return collectedResults

def readDistinctConnection(connectionType, semanticConnections, conceptLogic):
    return readDistinctConnections(connectionType, 1, semanticConnections, conceptLogic)[0]

def writeDistinctConnections(concepts, connectionType, conceptLogic, previousConnections = frozenset([])):
    predConcept = ensureConcept(connectionType, conceptLogic)
    return frozenset([
        *previousConnections,
        *[(None, predConcept, concept) for concept in concepts]
    ])

def writeDistinctConnection(concept, connectionType, conceptLogic, previousConnections = frozenset([])):
    return writeDistinctConnections([concept], connectionType, conceptLogic, previousConnections)

class SetConcept(metaclass=CodedConceptClass):
    """
    A set containing multiple concepts.
    It uses python frozensets as concept content
    """
    def getContentFromConnections(semanticConnections, conceptLogic):
        countConcept = readDistinctConnection(hasSetCount, semanticConnections, conceptLogic)
        if not countConcept.implementation == NumberConcept:
            raise semanticConnectionsNotValid()
        count =  countConcept.content
        if not (count % 1 == 0 and count > -1):
            raise semanticConnectionsNotValid()
        return frozenset(readDistinctConnections(hasSetEntry, count, semanticConnections, conceptLogic))

    def getConnectionsFromContent(content, conceptLogic):
        connections = writeDistinctConnection(NumberConcept(len(content), conceptLogic), hasSetCount, conceptLogic)
        return writeDistinctConnections(content, hasSetEntry, conceptLogic, connections)

    def contentValid(content, conceptLogic):
        return isinstance(content, frozenset) and all([isinstance(concept, Concept) for concept in content])
    

hasSubjectOfConnection = basicIdentities("hasSubjectOfConnection")
hasPredicateOfConnection = basicIdentities("hasPredicateOfConnection")
hasObjectOfConnection = basicIdentities("hasObjectOfConnection")
hasConnectionSelfReferenceCount = basicIdentities("hasConnectionSelfReferenceCount")
class ConnectionConcept(metaclass=CodedConceptClass):
    """
    A concept representing a single semantic connection
    It has an triple of subject predicate and object concepts as conceptContent where at least one of those is None
    """
    def getContentFromConnections(semanticConnections, conceptLogic):
        # Get subject predicate and object
        subjcon = hasSubjectOfConnection.getConcept(conceptLogic)
        subj = [z for x, y, z in semanticConnections if x == None and y == subjcon ]
        if len(subj) > 1: raise semanticConnectionsNotValid()
        predcon = hasPredicateOfConnection.getConcept(conceptLogic)
        pred = [z for x, y, z in semanticConnections if x == None and y == predcon ]
        if len(pred) > 1: raise semanticConnectionsNotValid()
        objcon = hasObjectOfConnection.getConcept(conceptLogic)
        obj = [z for x, y, z in semanticConnections if x == None and y == objcon ]
        if len(obj) > 1: raise semanticConnectionsNotValid()
        # Get target and actual number of self references in this connection and raise exception if they dont match
        targetSelfReferenceCount = readDistinctConnection(hasConnectionSelfReferenceCount, semanticConnections, conceptLogic).content
        actualSelfReferenceCount = 3 - len(subj) - len(pred) - len(obj)
        if targetSelfReferenceCount > actualSelfReferenceCount:
            raise semanticConnectionsNotValid()
        if targetSelfReferenceCount < actualSelfReferenceCount:
            raise semanticConnectionsNotSufficient()
        # Build and return the semantic connection
        return (subj[0] if subj else None, pred[0] if pred else None, obj[0] if obj else None)
    
    def getConnectionsFromContent(content, conceptLogic):
        connections = set()
        if content[0] != None:
            connections.add((None, hasSubjectOfConnection.getConcept(conceptLogic), content[0]))
        if content[1] != None:
            connections.add((None, hasPredicateOfConnection.getConcept(conceptLogic), content[1]))
        if content[2] != None:
            connections.add((None, hasObjectOfConnection.getConcept(conceptLogic), content[2]))
        selfReferenceCount = 3 - sum([x != None for x in content])
        connections.add((None, hasConnectionSelfReferenceCount.getConcept(conceptLogic), NumberConcept(selfReferenceCount, conceptLogic)))
        return frozenset(connections)

    def contentValid(content, conceptLogic):
        if not isinstance(content, tuple):
            return False
        if not len(content) == 3:
            return False
        if sum([x == None for x in content]) == 0:
            return False
        if any([x != None and not isinstance(x, Concept) for x in content]):
            return False
        return True
    
connectionsHasConnection = basicIdentities("connectionsHasConnection")
connectionsHasConnectionCount = basicIdentities("connectionsHasConnectionCount")
    
class ConnectionsConcept(metaclass=CodedConceptClass):

    def getContentFromConnections(semanticConnections, conceptLogic):
        # Get number of connnections
        countConcept = readDistinctConnection(connectionsHasConnectionCount, semanticConnections, conceptLogic)
        if not countConcept.implementation == NumberConcept:
            raise semanticConnectionsNotValid()
        count =  countConcept.content
        if not (count % 1 == 0 and count > -1):
            raise semanticConnectionsNotValid()
        # Get connections
        contentConnections = readDistinctConnections(connectionsHasConnection, count, semanticConnections, conceptLogic)
        connectionConceptClass = ConnectionConcept.getConcept(conceptLogic)
        if not all([getConceptClass(x) == connectionConceptClass for x in contentConnections]):
            raise semanticConnectionsNotValid()
        # Create semanticConnections frozenset and return it
        return frozenset([x.content for x in contentConnections])
    
    def getConnectionsFromContent(content, conceptLogic):
        # Get the ConnectionConcepts
        concepts = [ConnectionConcept(x, conceptLogic) for x in content]
        # Write the connections
        connections = writeDistinctConnection(NumberConcept(len(content), conceptLogic), connectionsHasConnectionCount, conceptLogic)
        return writeDistinctConnections(concepts, connectionsHasConnection, conceptLogic, connections)
    
    def contentValid(content, conceptLogic):
        if not isinstance(content, frozenset):
            return False
        if not all([isinstance(x, tuple) and len(x) == 3 and not all([y != None for y in x]) and all([y == None or isinstance(y, Concept) for y in x]) for x in content]):
            return False
        return True
    
    def getContentFromPythonObject(content, conceptLogic):
        return frozenset([(*[None if y == None else ensureConcept(y, conceptLogic) for y in x],) for x in content])
    
    
        


#class listConcept(metaclass=CodedConceptClass):
#    """
#    A CodedConceptIdentity that implements conceptList (concepts representing tuples of concepts).
#    It uses python tuples as ConceptContent.
#    """
#    def getContentFromConnections(pairs, conceptLogic):
#        return () # TODO: implement
#
#    def getConnectionsFromContent(content, conceptLogic):
#        return () # TODO: implement
#
#    def contentValid(content, conceptLogic):
#        return type(content) == tuple and all([type(concept) == Concept for concept in content])