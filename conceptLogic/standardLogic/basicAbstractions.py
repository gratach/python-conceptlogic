from .standardConceptImplementation import CodedConceptClass, getConceptClass
from ..conceptLogic.conceptLogic import Concept, semanticConnectionsNotSufficient, semanticConnectionsNotValid
from .basicDataConcepts import uuidIdentity, NumberConcept, UUIDConcept, identityNamespace
from .basicConstructedConcepts import readDistinctConnection, writeDistinctConnection

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
        connections = readDistinctConnection(constructedAbstractionHasConnections, semanticConnections, conceptLogic).content
        connectio

def isAbstractConcept(concept):
    if not isinstance(concept, Concept):
        return False
    # TODO This is a temporary solution. Change when GeneralConstructedConcepts with interfaces are done properly
    return getConceptClass(concept).identity in {ConstructedAbstraction, DirectAbstraction}