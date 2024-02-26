"""
This module contains the basic structures for the implementation of StandardLogic concepts.

As required by the ConceptLogic interface, every concept needs to have a ConceptContent and a ConceptImplementation.
The StandardLogic interface adds the requirement that every concept needs to have a conceptClass concept.
Additionally, every concept may have a conceptIdentity, which is used to identify it across different ConceptLogic objects.

In this documentation concepts, conceptClass concepts, conceptImplementations and conceptIdentities are often refered to by the same name so it is important to differentiate between them:
    * Specific conceptImplementations are referred to as "the <someName> implementation".
    * Specific conceptClass concepts are referred to as "the <someName> concept".
    * Concepts that are instances of a specific conceptClass concept are referred to as "a <someName> concept" or "the <someName> concept, that <unambiguousDescription>".
    * ConceptIdentities of specific conceptClass concepts are referred to as "the <someName> identity".

This module sets the requirements for two types of concepts:
    1) DataConcepts: Concepts that can only be defined by their content (or the data representing their content).
    2) ConstructedConcepts: Concepts that can be defined by their semanticConnections (and optionally their content).

Both types of concepts have a ConceptImplementation, that inherits from the StandardConceptImplementation class:
    1) DataConcepts have a DataConceptImplementation as ConceptImplementation.
        It also acts as the identity of the specific dataConceptClass concept, that is the conceptClass of all concepts that use this DataConceptImplementation as ConceptImplementation.
            The dataConceptClass concept is itself a dataConceptClass concept, that uses the dataConceptClass implementation.
    2) ConstructedConcepts have one of the two subclasses of ConstructedConceptImplementation as ConceptImplementation:
        a) GeneralConstructedConceptImplementation: A general ConstructedConceptImplementation which is used for all ConstructedConcepts with no specified functionality.
           This class has only one instance: generalConstructedConceptImplementation.
        b) SpecifiedConstructedConceptImplementation: A ConstructedConceptImplementation with a specified functionality, that is adapted to the concepts that use it.

While in the case of DataConcepts, the ConceptImplementation acts as the identity of the conceptClass, ConstructedConcepts have conceptClasses, that are not directly associated with their ConceptImplementations.
Instead, ConstructedConcepts have constructedConceptClass concepts as conceptClasses.
constructedConceptClass concepts may have one of two ConceptImplementations:
    1) GeneralConstructedConceptClassImplementation
    2) SpecifiedConstructedConceptClassImplementation

If a constructedConceptClass has a GeneralConstructedConceptClassImplementation as ConceptImplementation, all of its instances have the generalConstructedConceptImplementation as ConceptImplementation.
    In this case the constructedConceptClass concept has its FundamentalSemanticConnections as ConceptContent.
If a constructedConceptClass has a SpecifiedConstructedConceptClassImplementation as ConceptImplementation, it must have a ConstructedConceptClassIdentity as ConceptContent.
    A ConstructedConceptClassIdentity has a list of ConstructedConceptImplementation objects as implementations attribute.
    All instances of the constructedConceptClass must have the first ConstructedConceptImplementation object in the list that supports their FundamentalSemanticConnections as ConceptImplementation.
    The ConstructedConceptClassIdentity is also the conceptIdentity of that constructedConceptClass concept that has it as ConceptContent.

All constructedConceptClass concepts are instances of the constructedConceptClass concept which is itself a constructedConceptClass concept.
The constructedConceptClass concept has a SpecifiedConstructedConceptClassImplementation as ConceptImplementation and a ConstructedConceptClassIdentity (that is also called constructedConceptClass) as ConceptContent and ConceptIdentity.
The constructedConceptClass identity has a list of the SpecifiedConstructedConceptClassImplementation and the GeneralConstructedConceptClassImplementation as implementations attribute.


This module also introduces the CodedConceptClass meta class, to allow the definition of DataConceptImplementations and ConstructedConceptClassIdentity by using python classes.
Which of these two types is created is determined by the methodes and class variables that are implemented by the python class.

Therefore the following methodes are used:
    The data conversion methodes:
        def getContentFromData(data, conceptLogic):
            # Convert the data to the content of the concept
        def getDataFromContent(content, conceptLogic):
            # Convert the content of the concept to data
    The connection conversion methodes:
        def getContentFromConnections(conceptLogic, semanticConnections):
            # Convert the semanticConnections to the content of the concept
        def getConnectionsFromContent(conceptLogic, content):
            # Convert the content of the concept to semanticConnections
    The argument conversion methode:
        def getContentFromArguments(conceptLogic, *args, **kwargs):
            # Convert the args and kwargs to the conntent of the concept

A DataConceptImplementation can be created in the following way:

    class nameOfConceptClass(metaclass=CodedConceptClass):
        # The definition of the data conversion methodes
        # Optionally the definition of a content valid methode
        # Optionally the definition of the argument conversion methode
        # Optionally an arbitrary number of concept methodes and class methodes

A ConstructedConceptClassIdentity can be created eather with a single ConstructedConceptImplementation... :

        class nameOfConceptClass(metaclass=CodedConceptClass):
            # The definition of the conection conversion methodes
            semanticConnectionIdentities = semanticConnectionIdentitiesOfTheConstructedConceptClass
            implementationName = "nameOfTheImplementation" # Optional (defaults to nameOfTheConceptClass + "Implementation")
            # Optionally the definition of a content valid methode
            # Optionally the definition of the data conversion methodes
            # Optionally the definition of the argument conversion methode
            # Optionally an arbitrary number of concept methodes and class methodes

    ...or with multiple ConstructedConceptImplementations:

        class nameOfConceptClass(metaclass=CodedConceptClass):
            semanticConnectionIdentities = semanticConnectionIdentitiesOfTheConstructedConceptClass
            # An arbitrary number of the following implementation definitions:
            @CodedImplementation
            class nameOfTheImplementation:
                # The definition of the conection conversion methodes
                # Optionally the definition of a content valid methode
                # Optionally the definition of the data conversion methodes
                # Optionally the definition of the argument conversion methode
                # Optionally an arbitrary number of concept methodes
            # Optionally an arbitrary number of concept methodes and class methodes

Concept methodes and conceptClass methodes are defined in the following way:

    @ConceptMethode
    def nameOfMethode(content, conceptLogic, *arguments):
        # Implement the methode
    @ConceptClassMethode
    def nameOfClassMethode(conceptClass, conceptLogic, *arguments):
        # Implement the class methode
"""



import uuid
from ..conceptLogic.conceptLogic import ConceptImplementation, ConceptIdentity, semanticConnectionsNotValid, Concept, ConceptLogic, semanticConnectionsNotSufficient
from .standardLogic import StandardNamespace as sn
from .standardTools import ConceptGetter, SimpleConceptGetter, emptyConceptIdentity, SimpleConceptIdentity, ensureConcept


class StandardLogic(ConceptLogic):
    """
    StandardLogic is a ConceptLogic that defines the evaluateTripleFunction and the getConceptImplementationFromSemanticConnectionsFunction
    """
    def __init__(self, initialConceptIdentities = []):
        super().__init__(StandardLogic._myEvaluateTripleFunction, StandardLogic._myGetConceptImplementationAndContentFromConnectionsFunction, initialConceptIdentities)
        # Load the concepts of the identities from the StandardNamespace and make them permanent by adding them to the _standardConcepts set.
        self._standardConcepts = set()
        for pythonObject in sn.values():
            if isinstance(pythonObject, ConceptIdentity):
                self._standardConcepts.add(self.getConceptFromIdentity(pythonObject))
        self.activate()

    @staticmethod
    def _myEvaluateTripleFunction(self, subject, predicate, object):
        pass

    @staticmethod
    def _myGetConceptImplementationAndContentFromConnectionsFunction(conceptLogic, semanticConnections):
        # Get the concept class
        instanceOfPred = isInstanceOf.getConcept(conceptLogic)
        conceptClasses = [z for x, y, z in semanticConnections if x == None and y == instanceOfPred]
        if len(conceptClasses) == 0:
            raise semanticConnectionsNotSufficient()
        if len(conceptClasses) > 1:
            raise semanticConnectionsNotValid()
        conceptClass = conceptClasses[0]
        if conceptClass.implementation == ConstructedConceptClass.implementations[0]:
            # The conceptClass is an SpecifiedConstructedConceptClass
            return conceptClass.identity.getImplementationAndContentFromConnections(semanticConnections, conceptLogic)
        elif conceptClass.implementation == ConstructedConceptClass.implementations[1]:
            # The conceptClass is an GeneralConstructedConceptClass
            raise "Not Implemented"
        else:
            raise semanticConnectionsNotValid()


class constructrionArgumentNotValid(Exception): # Exception raised by getContentFromPythonObject function
    def __init__(self):
        super().__init__("The python construction argument is not valid.")

_standardConceptImplementationByUUID = {}
_UUIDByStandardConceotImplementation = {}
_StandardConceptImplementationNamespaceUUID = uuid.uuid3(uuid.NAMESPACE_DNS, "StandardConceptImplementationNamespaceUUID")
class StandardConceptImplementation(ConceptImplementation):
    """
    A StandardConceptImplementation object is a ConceptImplementation that has an uuid assigned to it.
    The uuid is generated from the name and version of the StandardConceptImplementation.
    Besides the function arguments of ConceptImplementation, the constructor of StandardConceptImplementation also takes:
        name: The name of the StandardConceptImplementation.
        version: The version of the StandardConceptImplementation.
        and optionally:
            getContentFromPythonObject: A function that converts a python object to the ConceptContent.
                This does not have to be invertible.
    There are potentially 4 construction modes for concepts with this StandardConceptImplementation:
        1) pythonObject: The concept is constructed from a python object.
        2) semanticConnections: The concept is constructed from semanticConnections.
        3) content: The concept is constructed from content.
        4) data: The concept is constructed from data.
    """
    # The construction modes
    pythonObjectMode, semanticConnectionsMode, contentMode, dataMode = "pythonObject", "semanticConnections", "content", "data"

    def __init__(self, name, version, 
                 getContentFromData = None, getDataFromContent = None,
                 getContentFromConnections = None, getConnectionsFromContent = None,  
                 contentValid = None, initializeConcept = None,
                 implementationSupported = None, getConceptAttribute = None, callConcept = None,
                 getContentFromPythonObject = None, prefaredConstructionMode = None, getConceptClassFromContent = None,
                 getNameFromContent = None):
        self.implementationName = name
        self.version = version
        self.getContentFromPythonObject = getContentFromPythonObject
        self.getConceptClassFromContent = getConceptClassFromContent
        self.getNameFromContent = getNameFromContent
        self._prefaredConstructionMode = prefaredConstructionMode
        # Generate a UUID for this instance
        self.uuid = uuid.uuid3(_StandardConceptImplementationNamespaceUUID, name + " " + version)
        # Check if there is already a StandardConceptImplementation with this uuid
        if self.uuid in _standardConceptImplementationByUUID:
            raise Exception("There is already a RegisteredConceptImplementation with this uuid.")
        # Add this instance to the dictionarys
        _standardConceptImplementationByUUID[self.uuid] = self
        _UUIDByStandardConceotImplementation[self] = self.uuid
        # Initialize the ConceptImplementation
        super().__init__(getContentFromData = getContentFromData, getDataFromContent = getDataFromContent, 
                         getContentFromConnections =  getContentFromConnections, getConnectionsFromContent = getConnectionsFromContent,  
                         contentValid = contentValid, initializeConcept = initializeConcept,
                         implementationSupported = implementationSupported, getConceptAttribute = getConceptAttribute, callConcept = callConcept)

    
    def constructionModeSupported(self, constructionMode):
        """
        This function returns True if the given constructionMode is supported by this StandardConceptImplementation.
        """
        if constructionMode == self.pythonObjectMode:
            return self.getContentFromPythonObject != None
        if constructionMode == self.semanticConnectionsMode:
            return self.getConnectionsFromContent != None
        if constructionMode == self.contentMode:
            return self.getContentFromConnections != None
        if constructionMode == self.dataMode:
            return self.getContentFromData != None
        return False

    @property
    def prefaredConstructionMode(self):
        """
        Returns the _prefaredConstructionMode attribute of this StandardConceptImplementation if it is not None.
        Otherwise it returns the first supported constructionMode in the following order:
            pythonObject
            semanticConnections
            content
        """
        if self._prefaredConstructionMode != None:
            return self._prefaredConstructionMode
        if self.getContentFromPythonObject != None:
            return self.pythonObjectMode
        if self.getContentFromConnections != None:
            return self.semanticConnectionsMode
        return self.contentMode
    
    def construct(self, constructionArgument, conceptLogic, constructionMode = None):
        """
        This function constructs a concept from the given constructionMode and constructionArguments.
        """
        # Get the prefared construction mode if no construction mode is given
        if constructionMode == None:
            constructionMode = self.prefaredConstructionMode
        # Construct the concept
        if constructionMode == self.pythonObjectMode:
            return conceptLogic.getConceptFromContent(self, self.getContentFromPythonObject(constructionArgument))
        if constructionMode == self.semanticConnectionsMode:
            return conceptLogic.getConceptFromContent(self, self.getContentFromConnections(constructionArgument), conceptLogic)
        if constructionMode == self.contentMode:
            return conceptLogic.getConceptFromContent(self, constructionArgument)
        if constructionMode == self.dataMode:
            return conceptLogic.getConceptFromContent(self, self.getContentFromData(constructionArgument), conceptLogic)
        raise Exception("The given constructionMode is not supported by this StandardConceptImplementation.")
    
    def __call__(self, constructionArgument, standardLogic = None):
        """
        This function returns a Concept that is constructed from the constructionArgument if the standardLogic argument is given.
        Else a ConceptGetter is returned, that can create such Concept.
        """
        if self.getContentFromPythonObject != None:
            contentCreationFunction = lambda standardLogic : self.getContentFromPythonObject(constructionArgument, standardLogic)
        else:
            contentCreationFunction = lambda standardLogic : constructionArgument
        conceptCreationFunction = lambda standardLogic : standardLogic.getConceptFromContent(self, contentCreationFunction(standardLogic))
        if standardLogic != None:
            return conceptCreationFunction(standardLogic)
        return SimpleConceptGetter(conceptCreationFunction)
    
    def __repr__(self):
        return "ConceptImplementation " + self.implementationName + " " + self.version
    


class DataConceptImplementation(StandardConceptImplementation, ConceptIdentity, ConceptGetter):
    """
    A DataConceptImplementation object is the ConceptImplementation of a dataConcept.
    It is the identity of the dataConceptClass concept, that is the conceptClass of all Concept instances that use this DataConceptImplementation.
    """
    def __new__(cls, *args, seedObject = None, **kwargs):
        if seedObject != None:
            assert isinstance(seedObject, ConceptIdentity)
            seedObject.__class__ = DataConceptImplementation
            return seedObject
        return object.__new__(cls)
    def __init__(self, name,  version,
                 getContentFromData, getDataFromContent, 
                 contentValid = None, initializeConcept = None,
                 implementationSupported = None, getConceptAttribute = None, callConcept = None,
                 getContentFromPythonObject = None, seedObject = None, getNameFromContent = None):
        self.identityName = name
        # Initialize the RegisteredConceptImplementation
        StandardConceptImplementation.__init__(self, name + "Implementation", version,
                         getContentFromData = getContentFromData, getDataFromContent = getDataFromContent, 
                         getContentFromConnections=None, getConnectionsFromContent=None,
                         contentValid=contentValid, initializeConcept=initializeConcept,
                         implementationSupported=implementationSupported, getConceptAttribute=getConceptAttribute, callConcept=callConcept,
                         getContentFromPythonObject=getContentFromPythonObject, getNameFromContent=getNameFromContent)
        # Initialize the ConceptIdentity. Use dataConceptClass as the conceptIdentity. Use a self returning function as the contentCreationFunction
        ConceptIdentity.__init__(self, DataConceptClass, lambda conceptLogic: self)

    def getConcept(self, conceptLogic):
        return conceptLogic.getRawConceptFromIdentity(self)

class ConstructedConceptImplementation(StandardConceptImplementation):
    """
    A ConstructedConceptImplementation object is the ConceptImplementation of a constructedConcept.
    It has two subclasses:
        1) GeneralConstructedConceptImplementation: A general ConstructedConceptImplementation which is used for all ConstructedConcepts with no specified functionality.
              This class has only one instance: generalConstructedConceptClassImplementation.
        2) SpecifiedConstructedConceptImplementation: A ConstructedConceptImplementation with a specified functionality, that is adapted to the concepts that use it.
    """
    def __init__(self, name,  version,
                 getContentFromConnections, getConnectionsFromContent, 
                 getContentFromData = None, getDataFromContent = None, 
                 contentValid = None, initializeConcept = None,
                 implementationSupported = None, getConceptAttribute = None, callConcept = None,
                 getContentFromPythonObject = None, getConceptClassFromContent = None, getNameFromContent = None):
        # Initialize the RegisteredConceptImplementation
        StandardConceptImplementation.__init__(self, name, version,
                         getContentFromData=getContentFromData, getDataFromContent=getDataFromContent, 
                         getContentFromConnections=getContentFromConnections, getConnectionsFromContent=getConnectionsFromContent, 
                         contentValid=contentValid, initializeConcept=initializeConcept,
                         implementationSupported=implementationSupported, getConceptAttribute=getConceptAttribute, callConcept=callConcept,
                         getContentFromPythonObject=getContentFromPythonObject, getConceptClassFromContent=getConceptClassFromContent,
                         getNameFromContent=getNameFromContent)

    def getConcept(self, conceptLogic):
        return conceptLogic.getRawConceptFromIdentity(self)

generalConstructedConceptImplementation = None
class GeneralConstructedConceptImplementation(ConstructedConceptImplementation):
    """
    There is only one GeneralConstructedConceptClassImplementation object "generalConstructedConceptClassImplementation", which is the implementation of all GeneralConstructedConcepts.
    Concepts with this implementation have SemanticConnections as ConceptContent which have to contain the (None, isInstanceOf, <conceptClass>) triplet.
    This triple is used to assign the ConceptClass to all concepts with this implementation.
    """
    def __init__(self):
        global generalConstructedConceptImplementation
        if generalConstructedConceptImplementation != None:
            raise Exception("Only one GeneralConstructedConceptClassImplementation object 'generalConstructedConceptClassImplementation' can be created")
        generalConstructedConceptImplementation = self
        super().__init__("generalConstructedConceptClassImplementation", "0.0", self.getContentFromConnections, self.getConnectionsFromContent)

    def getContentFromConnections(self, semanticConnections, conceptLogic):
        # TODO Filter semanticConnections
        return semanticConnections
    
    def getConnectionsFromContent(self, content, conceptLogic):
        return content

    def getConceptClassFromContent(self, content, conceptLogic):
        return [obj for sub, pred, obj in content if sub == None and pred.identity == isInstanceOf][0]
    
    def getConcept(self, conceptLogic):
        pass
generalConstructedConceptImplementation = GeneralConstructedConceptImplementation()



class SpecifiedConstructedConceptImplementation(ConstructedConceptImplementation):
    """
    A SpecifiedConstructedConceptClassImplementation object is a ConstructedConceptImplementation with a specified functionality, that is adapted to the concepts that use it.
    Each SpecifiedConstructedConceptClassImplementation object belongs to a ConstructedConceptClassIdentity object.
    """
    def __init__(self, name, version, getContentFromConnections, getConnectionsFromContent, 
                 getContentFromData = None, getDataFromContent = None, contentValid=None, getNameFromContent=None, getContentFromPythonObject=None):
        # Initialize the ConceptIdentity. Use specificConstructedConceptClassImplementation as the conceptImplementation (empty object on the first run). Use a self returning function as the contentCreationFunction
        ConceptIdentity.__init__(self, SpecifiedConstructedConceptImplementation, lambda conceptLogic: self)
        # Initialize the ConstructedConceptClassIdentity
        self.name = name
        self.version = version
        self.classIdentity = None
        self._innerGetConnectionsFromContent = getConnectionsFromContent
        super().__init__(name, version,
                         getContentFromConnections=getContentFromConnections, getConnectionsFromContent=self._wrappedGetConnectionsFromContent,
                          getContentFromData=getContentFromData, getDataFromContent=getDataFromContent, contentValid=contentValid,
                          getNameFromContent=getNameFromContent, getContentFromPythonObject=getContentFromPythonObject)
        
    def _wrappedGetConnectionsFromContent(self, content, standardLogic):
        return frozenset([(None, isInstanceOf.getConcept(standardLogic), self.classIdentity.getConcept(standardLogic)),
                          *self._innerGetConnectionsFromContent(content, standardLogic)])
    
    def getConceptImplementationFromSemanticConnections(self, semanticConnections):
        """
        This function returns a ConstructedConceptImplementation object that supports the given semanticConnections.
        If no ConstructedConceptImplementation object supports the given semanticConnections, this function raises an Exception.
        """
        # TODO: Implement
        pass

    def getConcept(self, conceptLogic):
        # TODO: Implement
        pass

_constructedConceptClassIdentityBySemanticConnectionIdentities = {}
_constructedConceptClassIdentityByUUID = {}
_UUIDByConstructedConceptClassIdentity = {}
_ConstructedConceptClassIdentityNamespaceUUID = uuid.uuid3(uuid.NAMESPACE_DNS, "ConstructedConceptClassIdentityNamespaceUUID")
class ConstructedConceptClassIdentity(ConceptIdentity):
    """
    A ConstructedConceptClassIdentity object is the ConceptIdentity of a constructedConceptClass concept.
    It resembles the ConceptContent of the one SpecifiedConstructedConceptClassImplementation, that is associated with it.
    """

    def __new__(cls, *args, seedObject = None):
        if seedObject != None:
            assert isinstance(seedObject, ConceptIdentity)
            seedObject.__class__ = ConstructedConceptClassIdentity
            return seedObject
        return object.__new__(cls)

    def __init__(self, implementations, semanticConnectionIdentities, name, version, seedObject = None): # TODO Finish definition
        self.implementations = implementations
        self.identityName = name
        self.version = version
        # Generate a UUID for this instance
        self.uuid = uuid.uuid3(_ConstructedConceptClassIdentityNamespaceUUID, name + " " + version)
        # Check if there is already a StandardConceptImplementation with this uuid
        if self.uuid in _constructedConceptClassIdentityByUUID:
            raise Exception("There is already a RegisteredConceptImplementation with this uuid.")
        # Add this instance to the dictionarys
        _constructedConceptClassIdentityByUUID[self.uuid] = self
        _UUIDByConstructedConceptClassIdentity[self] = self.uuid
        # Add this ConstructedConceptClassIdentity to all SpecifiedConstructedConceptImplementations
        for implementation in implementations:
            implementation.classIdentity = self
        # Add the (None, isInstanceOf, ConstructedConceptClass) triple if missing and make it a frozenset
        semanticConnectionIdentities = frozenset([*semanticConnectionIdentities, (None, isInstanceOf, ConstructedConceptClass)])
        # Initialize
        self.semanticConnectionIdentities = semanticConnectionIdentities
        global _constructedConceptClassIdentityBySemanticConnectionIdentities
        if semanticConnectionIdentities in _constructedConceptClassIdentityBySemanticConnectionIdentities:
            raise Exception("There is already a ConstructedConceptClassIdentity with the same SemanticConnections")
        _constructedConceptClassIdentityBySemanticConnectionIdentities[semanticConnectionIdentities] = self
        super().__init__(ConstructedConceptClass.implementations[0], lambda cl : self)

    def getImplementationAndContentFromConnections(self, connections, standardLogic):
        for implementation in self.implementations:
            try:
                return (implementation, implementation.getContentFromConnections(connections, standardLogic))
            except semanticConnectionsNotValid:
                continue
        raise semanticConnectionsNotValid()

    def __call__(self, constructionArgument, standardLogic = None):
        """
        This function returns a Concept that is constructed from the constructionArgument if the standardLogic argument is given.
        Else a ConceptGetter is returned, that can create such Concept.
        """
        def conceptCreationFunction(standardLogic):
            for implementation in self.implementations:
                if implementation.getContentFromPythonObject != None:
                    try:
                        return standardLogic.getConceptFromContent(implementation, implementation.getContentFromPythonObject(constructionArgument, standardLogic))
                    except constructrionArgumentNotValid:
                        continue
                if implementation.contentValid(constructionArgument, standardLogic):
                    return standardLogic.getConceptFromContent(implementation, constructionArgument)
            raise constructrionArgumentNotValid 
            
        if standardLogic != None:
            return conceptCreationFunction(standardLogic)
        return SimpleConceptGetter(conceptCreationFunction)
    
    def getConcept(self, standardLogic):
        return standardLogic.getRawConceptFromIdentity(self)


isInstanceOf = emptyConceptIdentity()


_globalMarkedClassContentCount = 0

class _MarkedClassContent:
    """
    A class to wrap the contents of python classes and add metadata to them
    """
    def __init__(self, content, metadata):
        self.content = content
        self.metadata = metadata
        global _globalMarkedClassContentCount
        self.orderID = _globalMarkedClassContentCount
        _globalMarkedClassContentCount += 1

def CodedImplementation(func):
    """
    A decorator to mark the class structures within the codedConceptClass that are used to group the implementation methodes of a single SpecifiedConstructedConceptClassImplementation within the ConstructedConceptClassIdentity.
    """
    return _MarkedClassContent(func, "CodedImplementation")

def ConceptMethode(func):
    """
    A decorator to mark the methodes of the concepts
    """
    return _MarkedClassContent(func, "ConceptMethode")

def ConceptClassMethode(func):
    """
    A decorator to mark the methodes of concept classes
    """
    return _MarkedClassContent(func, "ConceptClassMethode")

class CodedConceptClass(type):
    """
    A metaclass that is used to create ConceptClass identity objects by defining python classes.
    Depending on the defined implementation functions and classes the created object can be a DataConceptImplementation or one of the two ConstructedConceptClassImplementation classes GeneralConstructedConceptClassImplementation or SpecifiedConstructedConceptClassImplementation.
    """
    def __new__(cls, clsname, bases, attrs):
        """
        The function that is called when a new class is created.
        It returns:
            1) A DataConceptImplementation if the data conversion methodes are defined
            2) A ConstructedConceptClassIdentity in all other cases
        """
        # Extract all relevant attributes

        # Extract all marked class contents
        markedClassContents = [] # A list of tuples of form (name, content, metadata, orderId)
        for name, content in attrs.items():
            if type(content) == _MarkedClassContent:
                markedClassContents.append((name, content.content, content.metadata, content.orderID))
        for name, x, y, z in markedClassContents:
            attrs.pop(name)
        # Sort the markedClassContents by orderID
        markedClassContents.sort(key = lambda x: x[3])
        # Group by metadata
        contentsByMetadata = {}
        for name, content, metadata, x in markedClassContents:
            if not metadata in contentsByMetadata:
                contentsByMetadata[metadata] = []
            contentsByMetadata[metadata].append((name, content))
        
        # Extract the version
        version = attrs.pop("version") if "version" in attrs else "0.0"

        # Extract the data conversion methodes if they exist
        getContentFromData = attrs.get("getContentFromData")
        getDataFromContent = attrs.get("getDataFromContent")
        if not (getContentFromData == None) == (getDataFromContent == None):
            raise Exception("Both or none data conversion methodes need to be defined")
        if getContentFromData != None:
            attrs.pop("getContentFromData"); attrs.pop("getDataFromContent")
        
        # Extract the connection conversion methodes if they exist
        getContentFromConnections = attrs.get("getContentFromConnections")
        getConnectionsFromContent = attrs.get("getConnectionsFromContent")
        if not (getContentFromConnections == None) == (getConnectionsFromContent == None):
            raise Exception("Both or none connection conversion methodes need to be defined")
        if getContentFromConnections != None:
            attrs.pop("getContentFromConnections"); attrs.pop("getConnectionsFromContent")

        # Extract the argument conversion methode if it exists
        getContentFromPythonObject = attrs.pop("getContentFromPythonObject") if "getContentFromPythonObject" in attrs else None

        # Extract the content to name conversion methode if it exists
        getNameFromContent = attrs.pop("getNameFromContent") if "getNameFromContent" in attrs else lambda content, conceptLogic : clsname + "Instance"

        # Extract the contentValid methode if it exists
        contentValid = attrs.pop("contentValid") if "contentValid" in attrs else None

        # Extract the SemanticConnections methode if it exists
        semanticConnectionIdentities = set(attrs.pop("semanticConnectionIdentities")) if "semanticConnectionIdentities" in attrs else None

        # Extract the seed object if exists
        seedObject = attrs.pop("seedObject") if "seedObject" in attrs else None

        # Extract all concept methodes
        conceptMethodes = {}
        for name, content in contentsByMetadata.pop("ConceptMethode") if "ConceptMethode" in contentsByMetadata else []:
            conceptMethodes[name] = content

        # Extract all concept class methodes
        conceptClassMethodes = {}
        for name, content in contentsByMetadata.pop("ConceptClassMethode") if "ConceptClassMethode" in contentsByMetadata else []:
            conceptClassMethodes[name] = content

        # Extract all CodedImplementations
        codedImplementations = []
        for name, content in contentsByMetadata.pop("CodedImplementation") if "CodedImplementation" in contentsByMetadata else []:

            CIAttrs = {dname : dvalue for dname, dvalue in content.__dict__.items() if not (dname.startswith("__") and dname.endswith("__"))}

            # Extract all relevant CodedImplementation attributes

            # Extract the connection conversion methodes if they exist
            CIGetContentFromConnections = CIAttrs.pop("getContentFromConnections") if "getContentFromConnections" in CIAttrs else None
            CIGetConnectionsFromContent = CIAttrs.pop("getConnectionsFromContent") if "getConnectionsFromContent" in CIAttrs else None

            # Extract the data conversion methodes if they exist
            CIGetContentFromData = CIAttrs.pop("getContentFromData") if "getContentFromData" in CIAttrs else None
            CIGetDataFromContent = CIAttrs.pop("getDataFromContent") if "getDataFromContent" in CIAttrs else None

            # Extract the argument conversion methode if it exists
            CIGetContentFromPythonObject = CIAttrs.pop("getContentFromPythonObject") if "getContentFromPythonObject" in CIAttrs else None

            # Extract the content to name conversion methode if it exists
            CIGetNameFromContent = attrs.pop("getNameFromContent") if "getNameFromContent" in attrs else lambda content, conceptLogic : clsname + "Instance"

            # Extract the content valid methode if it exists
            CIContentValid = CIAttrs.pop("contentValid") if "contentValid" in CIAttrs else None

            # Ectract the version if exists
            CIVersion = CIAttrs.pop("version") if "version" in CIAttrs else "0.0"
            
            # TODO concept methodes

            codedImplementations.append({
                "name" : name,
                "version" : CIVersion,
                "getContentFromConnections" : CIGetContentFromConnections,
                "getConnectionsFromContent" : CIGetConnectionsFromContent,
                "getContentFromData" : CIGetContentFromData,
                "getDataFromContent" : CIGetDataFromContent,
                "getContentFromPythonObject" : CIGetContentFromPythonObject,
                "getNameFromContent" : CIGetNameFromContent,
                "contentValid" : CIContentValid,
            })
        

        # Distinguish between different creation patterns and return the result
            
        # A DataConceptImplementation gets created if there are data conversion methodes but no connection conversion methodes and no CodedImplementations defined.
        if getContentFromData != None and getContentFromConnections == None and len(codedImplementations) == 0:
            return DataConceptImplementation(clsname, version, getContentFromData, getDataFromContent, contentValid, getContentFromPythonObject=getContentFromPythonObject, getNameFromContent=getNameFromContent , seedObject=seedObject)
        
        if semanticConnectionIdentities == None:
            # Temporary solution:
            identifyerIdentity = SimpleConceptIdentity(UUIDConcept,  uuid.uuid3(uuid.NAMESPACE_DNS, clsname + "_temporaryIdentifyer"), clsname + "_temporaryIdentifyer")
            semanticConnectionIdentities = [(None, identifiedByTemporarySolution, identifyerIdentity)]
            # raise Exception("For ConstructedConceptClassIdentities the semanticConnections have to be defined")
        
        if len(codedImplementations) == 0: # A ConstructedConceptClassIdentity gets created with a single ConstructedConceptImplementation 
            # Create a SpecifiedConstructedConceptImplementation
            implementations = [SpecifiedConstructedConceptImplementation(clsname + "Implementation", version, 
                                                                         getContentFromConnections=getContentFromConnections, getConnectionsFromContent=getConnectionsFromContent, 
                                                                         getContentFromData=getContentFromData, getDataFromContent=getDataFromContent,
                                                                         contentValid=contentValid, getNameFromContent=getNameFromContent, getContentFromPythonObject=getContentFromPythonObject)]
        else: # A ConstructedConceptClassIdentity gets created with a list of ConstructedConceptImplementations
            # Create the list of SpecifiedConstructedConceptImplementations
            implementations = []
            for codedImplementation in codedImplementations:
                implementations.append(SpecifiedConstructedConceptImplementation(codedImplementation["name"], codedImplementation["version"],
                                                                                 getContentFromConnections=codedImplementation["getContentFromConnections"], getConnectionsFromContent=codedImplementation["getConnectionsFromContent"],
                                                                                 getContentFromData=codedImplementation["getContentFromData"], getDataFromContent=codedImplementation["getDataFromContent"],
                                                                                 contentValid=codedImplementation["contentValid"], getNameFromContent=codedImplementation["getNameFromContent"],
                                                                                 getContentFromPythonObject=codedImplementation["getContentFromPythonObject"]))
        return ConstructedConceptClassIdentity(implementations, semanticConnectionIdentities, clsname, version, seedObject=seedObject)


DataConceptClass = emptyConceptIdentity()
class DataConceptClass(metaclass = CodedConceptClass):
    """
    The DataConceptImplementation that implements the ConceptClasses of all DataConcepts.
    It uses the DataConceptImplementation of the instances of the class as ConceptContent and stores it as data using its uuid.
    """

    seedObject = DataConceptClass
    
    def getContentFromData(data, conceptLogic):
        return _standardConceptImplementationByUUID[uuid.UUID(bytes.decode(data, "utf8"))]

    def getDataFromContent(content, conceptLogic):
        return bytes(str(_UUIDByStandardConceotImplementation[content]), "utf8")
    
    def contentValid(content, conceptLogic):
        return isinstance(content, DataConceptImplementation)

# Temporary solution TODO Remove
UUIDConcept = emptyConceptIdentity()
identifiedByTemporarySolution = emptyConceptIdentity()
temporaryConstructedConceptClassIdentifyer = emptyConceptIdentity()

ConstructedConceptClass = emptyConceptIdentity()
class ConstructedConceptClass(metaclass = CodedConceptClass):
    """
    The SpecifiedConstructedConceptClassIdentity that identifyes the ConstructedConceptClass concept, that is used as class concept for all constructed concepts.
    """

    seedObject = ConstructedConceptClass
    semanticConnectionIdentities = [(None, identifiedByTemporarySolution, temporaryConstructedConceptClassIdentifyer)]

    @CodedImplementation
    class SpecifiedConstructedConceptClassImplementation:
        """
        The implementations of ConstructedConceptsClasses which SpecifiedConstructedConcepts as instances.
        The respective ConstructedConceptsClass concepts have ConstructedConceptClassIdentities as ConceptContent.
        """

        def getContentFromConnections(connections, conceptLogic):
            # Get the SemanticConnectionIdentities from the SemanticConnections
            connectionIdentities = frozenset([
                (None if sub == None else sub.identity, None if pred == None else pred.identity, None if obj == None else obj.identity)
                for sub, pred, obj in connections
                if (sub == None or sub.identity != None) and (pred == None or pred.identity != None) and (obj == None or obj.identity != None)
            ])
            # If there is an SpecifiedConstructedConceptClassIdentity registered for this SemanticConnectionIdentities return it
            return _constructedConceptClassIdentityBySemanticConnectionIdentities.get(connectionIdentities)

        def getConnectionsFromContent(content, conceptLogic):
            cl = conceptLogic
            # Return the SemanticConnections that are created from the SemanticConnectionIdentities
            return frozenset([
                (None if sub == None else cl.getConceptFromIdentity(sub), None if pred == None else cl.getConceptFromIdentity(pred), None if obj == None else cl.getConceptFromIdentity(obj))
                for sub, pred, obj in content.semanticConnectionIdentities
            ])
    
        def getContentFromData(data, conceptLogic):
            return _constructedConceptClassIdentityByUUID[uuid.UUID(bytes.decode(data, "utf8"))]

        def getDataFromContent(content, conceptLogic):
            return bytes(str(_UUIDByConstructedConceptClassIdentity[content]), "utf8")
        
        def contentValid(content, conceptLogic):
            return isinstance(content, ConstructedConceptClassIdentity)
    
    @CodedImplementation
    class GeneralConstructedConceptClassImplementation:
        """
        The implementations of ConstructedConceptsClasses which GeneralConstructedConcepts as instances.
        The respective ConstructedConceptsClass concepts have semantic connections as concept content.
        """

        def getContentFromConnections(connections, conceptLogic):
            return connections

        def getConnectionsFromContent(content, conceptLogic):
            return content
        
        def contentValid(content, conceptLogic):
            # Check if the content has the format of a semanticConnections frozenset
            if not isinstance(content, frozenset):
                return False
            for semanticConnection in content:
                if not isinstance(semanticConnection, tuple) and len(semanticConnection) == 3:
                    return False
                hasNone = False
                for element in semanticConnection:
                    if element == None:
                        hasNone = True
                    else:
                        if not isinstance(element, Concept) or element.conceptLogic == conceptLogic:
                            return False
                if not hasNone:
                    return False
            return True
        
def getConceptClass(concept):
    if isinstance(concept.implementation, DataConceptImplementation):
        return concept.implementation.getConcept(concept.conceptLogic)
    elif isinstance(concept.implementation, SpecifiedConstructedConceptImplementation):
        return concept.implementation.classIdentity.getConcept(concept.conceptLogic)
    elif isinstance(concept.implementation, GeneralConstructedConceptImplementation):
        raise "Not Implemented" # TODO
    else:
        raise Exception("Implementation unknown")
    
def hasConceptClass(concept, conceptClass):
    return getConceptClass(concept) == ensureConcept(conceptClass, concept.conceptLogic)