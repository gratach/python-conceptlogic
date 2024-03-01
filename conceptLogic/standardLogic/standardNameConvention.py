from typing import Hashable
from ast import literal_eval
from uuid import UUID
from .standardLogicEnsemble import StandardNamespace as sn
from .standardConceptImplementation import StandardConceptImplementation, _standardConceptImplementationById, StandardLogic, getConceptName
from ..conceptLogic.conceptLogic import Concept

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
    
StandardLogic.nameConvention = StandardNameConvention
   