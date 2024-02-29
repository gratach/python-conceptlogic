from typing import Hashable
from ast import literal_eval
from uuid import UUID
from ..standardLogic.standardLogicEnsemble import StandardNamespace as sn
from ..standardLogic.standardConceptImplementation import StandardConceptImplementation, _standardConceptImplementationById
from .conceptLogic import Concept

class StandardNameConvention:
    """
    A class that converts concepts and conceptImplementations of a StandardLogic to name strings.
    It takes a namespaceDict as an argument and uses it for the selection of the names.
    """
    def __init__(self, namespaceDict = None):
        self._namespaceDict = namespaceDict if namespaceDict is not None else sn
        self._invertedNamespaceDict = {value if isinstance(value, Hashable) else id(value): name for name, value in self._namespaceDict.items()}
        self._conceptByName = {}
    def get(self, name):
        """
        Returns the python object that is represented by the given name.
        """
        return self._conceptByName.get(name, None)
    def __call__(self, pythonObject, proposedName = None):
        """
        Returns the name of the given concept.
        """
        # Check if the pythonObject is already in the dictionary
        if pythonObject in self._conceptByName:
            return self._conceptByName[pythonObject]
        # Get the name
        if proposedName is not None:
            name = proposedName
        else:
            if isinstance(pythonObject, Concept):
                name = getConceptName(pythonObject)
            elif isinstance(pythonObject, StandardConceptImplementation):
                name = pythonObject.implementationName
        # Change the name if it is already used
        testName = name
        i = 0
        while testName in self._conceptByName.values():
            i += 1
            testName = name + "_" + str(i)
        name = testName
        # Add the name to the dictionary and return it
        self._conceptByName[pythonObject] = name
        return name
    
def getConceptName(concept):
    if concept.identity != None:
        return concept.identity.identityName
    elif concept.implementation.getNameFromContent != None:
        return concept.implementation.getNameFromContent(concept.content, concept.conceptLogic)
    else:
        return concept.implementation.implementationName + "_instance"
    
    
def writeTriples(concepts, fs, 
                 stringNameConvention = None,
                 referenceOfHasData = "hasData", referenceOfHasImplementation = "hasImplementation", referenceOfHasImplementationId = "hasImplementationUUID"):
    """
    A function that writes a list of concepts to a file stream in a turtle like format.
    The stringNameConvention has to produce name strings with no newline charakters and no spaces
    """
    if stringNameConvention == None:
        stringNameConvention = StandardNameConvention()
    hasDataName = stringNameConvention(referenceOfHasData, referenceOfHasData)
    hasImplementationName = stringNameConvention(referenceOfHasImplementation, referenceOfHasImplementation)
    implementationUUIDName = stringNameConvention(referenceOfHasImplementationId, referenceOfHasImplementationId)
    # Get the exported SemanticData
    byteDataInfoByReference, referenceTriples = [*concepts][0].conceptLogic.exportSemanticData(concepts, stringNameConvention)
    # Get the implementations of concepts with data
    conceptImplementations = set([conceptImplementation for conceptImplementation, byteData in byteDataInfoByReference.values()])

    # collect the conceptImplementations with their uuids
    triples = []
    for conceptImplementation in conceptImplementations:
        implementationName = stringNameConvention(conceptImplementation)
        idstring = conceptImplementation.id.decode("utf-8")
        triples.append((implementationName, implementationUUIDName, repr(idstring)))
    # Sort alphabetically
    triples.sort(key = lambda x : (x[0].lower(), x[0], x[1].lower(), x[1], x[2].lower(), x[2]))
    # Write the conceptImplementations with their uuids
    for triple in triples:
        fs.write("{} {} {} .\n".format(*triple))
    fs.write("\n")

    # Collect the concepts with their data
    triples = []
    for reference, (conceptImplementation, byteData) in byteDataInfoByReference.items():
        implementationName = stringNameConvention(conceptImplementation)
        triples.append((reference, hasImplementationName, implementationName))
        triples.append((reference, hasDataName, repr(byteData.decode("utf-8"))))
    # Sort alphabetically
    triples.sort(key = lambda x : (x[0].lower(), x[0], x[1].lower(), x[1], x[2].lower(), x[2]))
    # Write the concepts with their data
    for triple in triples:
        fs.write("{} {} {} .\n".format(*triple))
    fs.write("\n")

    # Collect the triples
    triples = list(referenceTriples)
    # Sort alphabetically
    triples.sort(key = lambda x : (x[0].lower(), x[0], x[1].lower(), x[1], x[2].lower(), x[2]))
    # Write the triples
    for triple in triples:
        fs.write("{} {} {} .\n".format(*triple))

def readTriples(fs, standardLogic,
                 referenceOfHasData = "hasData", referenceOfHasImplementation = "hasImplementation", referenceOfHasImplementationUUID = "hasImplementationUUID"):
    """
    A function that reads a turtle like filestream and returns a dict that maps from all references of successfully loaded Concepts to the loaded Concepts.
    """
    lines = fs.read().split("\n")
    triples = []
    # Iterate over all lines
    for line in lines:
        linesplit = line.split(" ")
        if len(linesplit) < 4:
            if all([part == "" for part in linesplit]):
                continue
        elif linesplit[-1] == ".":
            sub = linesplit[0]
            pred = linesplit[1]
            obj = line[len(sub) + len(pred) + 2 : -2]
            # Escape quoted object strings
            if obj[0] == "'" or obj[0] == '"':
                obj = literal_eval(obj)
            # Add triple
            triples.append((sub, pred, obj))
            continue
        raise Exception("The not empty lines have to contain a triple terminated by ' .'")
    # Find the implementation Ids
    IdByName = {}
    for sub, obj in [(x, z) for x, y, z in triples if y == referenceOfHasImplementationUUID]:
        IdByName[sub] = obj.encode("utf8")
    # Find the implementations
    implementationByImplementationReference = {}
    for name, id in IdByName.items():
        if id in _standardConceptImplementationById:
            implementationByImplementationReference[name] = _standardConceptImplementationById[id]
    # Extract the data concepts
    implementationByConceptReference = {}
    for sub, obj in [(x, z) for x, y, z in triples if y == referenceOfHasImplementation]:
        implementationByConceptReference[sub] = implementationByImplementationReference[obj]
    dataByConceptReference = {}
    for sub, obj in [(x, z) for x, y, z in triples if y == referenceOfHasData]:
        dataByConceptReference[sub] = obj.encode("utf8")
    byteDataInfoByConceptReference = {ref : (implementationByConceptReference[ref], data) for ref, data in dataByConceptReference.items()}
    # Extract the constructed concepts
    referenceTriples = set([triple for triple in triples if not triple[1] in [referenceOfHasData, referenceOfHasImplementation, referenceOfHasImplementationUUID]])
    # Obtain and return the dict of loaded concepts
    semanticData = (byteDataInfoByConceptReference, referenceTriples)
    return standardLogic.importSemanticData(semanticData)
