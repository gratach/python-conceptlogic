import uuid
from .standardConceptImplementation import CodedConceptClass, SimpleConceptIdentity, isInstanceOf, UUIDConcept, identifiedByTemporarySolution, temporaryConstructedConceptClassIdentifyer

class NumberConcept(metaclass=CodedConceptClass):
    """
    A CodedConceptIdentity that implements NumberConcepts (concepts representing numbers).
    It uses python floats as ConceptContent.
    """
    def getContentFromData(data, conceptLogic):
        return float(data)

    def getDataFromContent(content, conceptLogic):
        return str(content).encode("utf-8")
    
    def contentValid(content, conceptLogic):
        return type(content) in {float, int}
    
    def getNameFromContent(content, conceptLogic):
        return "Number_" + str(content)

class StringConcept(metaclass=CodedConceptClass):
    """
    A CodedConceptIdentity that implements StringConcepts (concepts representing strings).
    It uses python string as concept content.
    """
    def getContentFromData(data, conceptLogic):
        return str(data, "utf-8")

    def getDataFromContent(content, conceptLogic):
        return content.encode("utf-8")
    
    def contentValid(content, conceptLogic):
        return type(content) == str

class UUIDConcept(metaclass=CodedConceptClass):
    """
    A CodedConceptIdentity that implements UUIDConcepts (concepts representing UUIDs).
    It uses python UUID objects as ConceptContent.
    """

    seedObject = UUIDConcept

    def getContentFromData(data, conceptLogic):
        return uuid.UUID(data.decode("utf-8"))

    def getDataFromContent(content, conceptLogic):
        return str(content).encode("utf-8")
    
    def contentValid(content, conceptLogic):
        return type(content) == uuid.UUID
    
    
def uuidIdentity(name, namespaceUUID = uuid.NAMESPACE_DNS, seedObject=None):
    return SimpleConceptIdentity(UUIDConcept, uuid.uuid3(namespaceUUID, name), name, seedObject=seedObject)

class identityNamespace:
    def __init__(self, name):
        self.name = name
        self.uuid = uuid.uuid3(uuid.NAMESPACE_DNS, name)
    def __call__(self, name, seedObject=None):
        return uuidIdentity(name, self.uuid, seedObject=seedObject)
    
isInstanceOf = uuidIdentity("isInstanceOf", seedObject=isInstanceOf)
identifiedByTemporarySolution = uuidIdentity("identifiedByTemporarySolution", seedObject=identifiedByTemporarySolution)
temporaryConstructedConceptClassIdentifyer = uuidIdentity("temporaryConstructedConceptClassIdentifyer", seedObject=temporaryConstructedConceptClassIdentifyer)
