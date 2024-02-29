import uuid
from .standardConceptImplementation import CodedConceptClass, SimpleConceptIdentity, isInstanceOf, UUIDConcept, identifiedByTemporarySolution, temporaryConstructedConceptClassIdentifyer, basicsPrefix, defalutPrefix


class NumberConcept(metaclass=CodedConceptClass):
    """
    A CodedConceptIdentity that implements NumberConcepts (concepts representing numbers).
    It uses python floats as ConceptContent.
    """
    prefix = basicsPrefix
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
    prefix = basicsPrefix
    def getContentFromData(data, conceptLogic):
        return str(data, "utf-8")

    def getDataFromContent(content, conceptLogic):
        return content.encode("utf-8")
    
    def contentValid(content, conceptLogic):
        return type(content) == str

class IdentityConcept(metaclass=CodedConceptClass):
    """
    A CodedConceptIdentity that implements IdentityConcepts
    It uses a bytes object as concept content.
    """
    prefix = basicsPrefix
    def getContentFromData(data, conceptLogic):
        return data

    def getDataFromContent(content, conceptLogic):
        return content
    
    def contentValid(content, conceptLogic):
        return type(content) == bytes

class BytesConcept(metaclass=CodedConceptClass):
    """
    A CodedConceptIdentity that implements BytesConcepts
    It uses a bytes object as concept content.
    """
    prefix = basicsPrefix
    def getContentFromData(data, conceptLogic):
        return data

    def getDataFromContent(content, conceptLogic):
        return content
    
    def contentValid(content, conceptLogic):
        return type(content) == bytes

class UUIDConcept(metaclass=CodedConceptClass):
    """
    A CodedConceptIdentity that implements UUIDConcepts (concepts representing UUIDs).
    It uses python UUID objects as ConceptContent.
    """
    prefix = basicsPrefix
    seedObject = UUIDConcept

    def getContentFromData(data, conceptLogic):
        return uuid.UUID(data.decode("utf-8"))

    def getDataFromContent(content, conceptLogic):
        return str(content).encode("utf-8")
    
    def contentValid(content, conceptLogic):
        return type(content) == uuid.UUID
    
    
def newIdentityConcept(name, prefix = defalutPrefix, seedObject=None):
    return SimpleConceptIdentity(IdentityConcept, prefix + name.encode("utf8"), name, seedObject=seedObject)
    
isInstanceOf = newIdentityConcept("isInstanceOf", basicsPrefix, seedObject=isInstanceOf)
identifiedByTemporarySolution = newIdentityConcept("identifiedByTemporarySolution", basicsPrefix, seedObject=identifiedByTemporarySolution)
temporaryConstructedConceptClassIdentifyer = newIdentityConcept("temporaryConstructedConceptClassIdentifyer", basicsPrefix, seedObject=temporaryConstructedConceptClassIdentifyer)
