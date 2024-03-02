"""
This module contais the basic functionality that is used to implement a ConceptLogic.
Each ConceptLogic instance can contain an arbitrary number of Concepts.
These Concepts are connected to a semantic network in a way that each (subject, predicate, object) triple of them is eather true or false.
Each Concept consists of references to a ConceptContent, a ConceptImplementation, the parent ConceptLogic and optionally a ConceptIdentity.
    The ConceptContent is a hashable python object that represents the content of the concept in the context of the ContentImplementation.
        During the initialization of the conceptLogic this property can also be undefined - e.g. when a circular reference inbetween concepts makes this necessary.
        In this case the concept is in a "raw" state.
    The ConceptImplementation is an object, that defines how the content of a concept is interpreted.
        It also defines the functionallity of the concept and methodes to load and safe the ConceptContent.
    The ConceptIdentity is used to identify Concepts across ConceptLogic objects.
        For each ConceptIdentity there can be only one Concept per ConceptLogic that references it as identity.
A concept within a ConceptLogic is unambiguousely defined by the ConceptContent and the ConceptImplementation. 
"""

import uuid
import weakref
import itertools

conceptLogicSet = set()
"""
    A global set of all ConceptLogic objects.
    """

class ConceptLogic:
    """
    A ConceptLogic object contains a set of Concept objects. It also provides a function to assign a truth value to a SemanticTriple object.
    The ConceptLogic class does not implement the full functionallity that it neads to work and should not be used by itself. 
    Instead it is used as a base class e.g. by the StandardLogic class.
    The Concepts are stored in the following way:
        The dict _loadedConcepts maps all supported ConceptImplementation objects to a WeakValueDictionary.
            The WeakValueDictionary maps all ConceptContent objects to a Concept object, that is not allowed to be in a "raw" state.
            This Concept object contains the ConceptContent object, the ConceptImplementation object and the ConceptLogic object.
        The dict _identifiedConcepts maps all supported ConceptImplementation objects to a dict.
            The dict maps all ConceptIdentity objects to a Concept object, that may or may not be in a "raw" state.
            This Concept object contains the ConceptIdentity object, the ConceptImplementation object, the ConceptLogic object and optionally the ConceptContent object.
    It also provides:
        evaluateTriple(subject, predicate, object) -> bool : A function that takes three Concept objects (subject, predicate, object) as arguments and returns a boolean.
            It returns True if the coresponding SemanticTriple object is true.
        getConceptFromSemanticConnections(connections) -> Concept : A function that takes an arbitrary number of semanticConnections as arguments and returns a Concept object.
            It returns a Concept object that contains the ConceptContent object that is created by the ConceptImplementation object from the semantic pairs.
        getSemanticConnectionsFromConcept(concept) -> set : A function that takes a Concept object as argument and returns a semanticConnections object
            It returns the semanticConnections that are created by the ConceptImplementation object from the ConceptContent object.
        getConceptFromContent(conceptImplementation, content) -> Concept : A function that takes a ConceptImplementation and a ConceptContent object as arguments and returns a Concept object.
            It returns a Concept object that contains the ConceptContent object, the ConceptImplementation object and the ConceptLogic object.
        getConceptFromIdentity(conceptIdentity) -> Concept : A function that takes a ConceptIdentity object as argument and returns a Concept object.
        getRawConceptFromIdentity(conceptIdentity) -> Concept : A function that takes a ConceptIdentity object as argument and returns a Concept object that may be in a "raw" state.
        exportSemanticData(exportedConcepts) -> SemanticData : A function that takes a set of Concept objects as argument and returns a SemanticData object.
        importSemanticData(semanticData) -> loadedConceptsByReference : A function that takes a SemanticData object as argument and returns a dict that maps from a reference to a Concept object.
        _versionString: A string that indicates the version of the ConceptLogic object.
        _versionUUID: A unique identifier for the ConceptLogic object. Created by uuid.uuid3(uuid.NAMESPACE_DNS, versionString).
        _evaluateTripleFunction: A function that takes this conceptLogic and tree Concept objects (subject, predicate, object) as arguments and returns a boolean.
        _getConceptImplementationAndContentFromSemanticConnectionsFunction: A function that takes this conceptLogic and semanticConnections as arguments and returns a (ConceptImplementation, ConceptContent) tupel.
        _nonRawImplementations: A set of ConceptImplementation objects that have been used for loading Concepts withouth a ConceptIdentity object.
            there are no raw Concepts allowed for these ConceptImplementation objects because they could have the same ConceptContent object as a already loaded Concept.
    """
    def __init__(self, evaluateTripleFunction, getConceptImplementationAndContentFromSemanticConnectionsFunction, initialConceptIdentities, versionString = "0.0.0"):
        self._loadedConcepts = {}
        self._identifiedConcepts = {}
        self._nonRawImplementations = set()
        self._evaluateTripleFunction = evaluateTripleFunction
        self._getConceptImplementationAndContentFromSemanticConnectionsFunction = getConceptImplementationAndContentFromSemanticConnectionsFunction
        self._versionString = versionString
        self._versionUUID = uuid.uuid3(uuid.NAMESPACE_DNS, versionString)
        self._activated = False
        conceptLogicSet.add(self)
        # Load the initial ConceptIdentities.
        for conceptIdentity in initialConceptIdentities:
            self.getConceptFromIdentity(conceptIdentity)

    def evaluateTriple(self, subject, predicate, object):
        """
        Returns True if the coresponding SemanticTriple object is true.
        """
        return self._evaluateTripleFunction(self, subject, predicate, object)
    
    def _getImplementationDicts(self, conceptImplementation):
        """
        Returns a tuple (conceptByIdentity, conceptByContent) of the dicts that are used to store Concepts of the given ConceptImplementation object.
        Raises an exception if the ConceptImplementation object is not supported by this ConceptLogic object.
        """
        conceptByIdentity = self._identifiedConcepts.get(conceptImplementation)
        conceptByContent = self._loadedConcepts.get(conceptImplementation)
        if conceptByIdentity == None or conceptByContent == None:
            assert conceptByIdentity == None and conceptByContent == None
            if conceptImplementation.implementationSupported != None and not conceptImplementation.implementationSupported(self):
                raise Exception("The ConceptImplementation " + str(conceptImplementation) + " is not supported by this ConceptLogic object.")
            conceptByIdentity = self._identifiedConcepts[conceptImplementation] = weakref.WeakValueDictionary()
            conceptByContent = self._loadedConcepts[conceptImplementation] = weakref.WeakValueDictionary()
        return (conceptByIdentity, conceptByContent)
    
    def getConceptFromContent(self, conceptImplementation, content):
        """
        Returns a Concept object that contains the ConceptContent object, the ConceptImplementation object and the ConceptLogic object.
        """
        if not conceptImplementation.contentValid(content, self):
            raise Exception("The content is not valid for the ConceptImplementation " + str(conceptImplementation) + ".")
        conceptsByContent = self._getImplementationDicts(conceptImplementation)[1]
        # If this is the first Concept with this ConceptImplementation and no ConceptIdentity to be loaded, make sure that all raw Concepts of the same ConceptImplementation are loaded first.
        if conceptImplementation not in self._nonRawImplementations:
            for conceptIdentity in self._identifiedConcepts.get(conceptImplementation, {}).keys():
                self.getConceptFromIdentity(conceptIdentity)
            self._nonRawImplementations.add(conceptImplementation)
        # If there is already a Concept with this ConceptContent, ConceptImplementation and ConceptLogic object, return it.
        if content in conceptsByContent:
            return conceptsByContent[content]
        # Return a new Concept object. The Concept constructor adds the Concept to the conceptsByContent dict and initializes the Concept object if the ConceptImplementation object has an initializeConcept function.
        return Concept(content, conceptImplementation, self)

    def getConceptFromData(self, conceptImplementation, byteData):
        """
        Returns a Concept object that contains the ConceptContent object, the ConceptImplementation object and the ConceptLogic object.
        """
        content = conceptImplementation.getContentFromData(byteData, self)
        return self.getConceptFromContent(conceptImplementation, content)
    
    def getConceptFromSemanticConnections(self, connections):
        """
        Returns a Concept object that contains the ConceptContent object that is created by the ConceptImplementation object from the SemanticConnection tuples.
        """
        implementation, content = self._getConceptImplementationAndContentFromSemanticConnectionsFunction(self, connections)
        return self.getConceptFromContent(implementation, content)
    
    def getConceptFromIdentity(self, conceptIdentity):
        """
        Returns a Concept object that contains the ConceptContent object, the ConceptImplementation object, the ConceptLogic object and the ConceptIdentity object.
        """
        implementation = conceptIdentity.implementation
        (conceptByIdentity, conceptByContent) = self._getImplementationDicts(implementation)
        if conceptIdentity in conceptByIdentity:
            # If there is already a Concept with this ConceptIdentity use it.
            concept = conceptByIdentity[conceptIdentity]
            if not concept.raw:
                # If the Concept is already loaded, return it.
                return concept
            # If the Concept is in a "raw" state, set the ConceptContent object.
            concept._content = conceptIdentity.contentCreationFunction(self)
            concept._raw = False
            # Add the Concept to the loadedConcepts dict.
            if content in conceptByContent:
                raise Exception("This Concept has more than one ConceptIdentity object.")
            conceptByContent[content] = concept
            # Initialize the Concept object if the ConceptImplementation object has an initializeConcept function.
            if implementation.initializeConcept != None:
                implementation.initializeConcept(concept)
        else:
            # If there is no Concept with this ConceptIdentity, create a new ConceptContent object.
            content = conceptIdentity.contentCreationFunction(self)
            # Check if a Concept with this content already exists
            if content in conceptByContent:
                concept = conceptByContent[content]
                # Add the identity to this concept
                concept._conceptIdentity = conceptIdentity
                conceptByIdentity[conceptIdentity] = concept
                # Return the already existing concept
                return concept
            else:
                # Return a new Concept object. The Concept constructor adds the Concept to the conceptsByIdentity dict and the conceptsByContent dict and initializes the Concept object if the ConceptImplementation object has an initializeConcept function.
                return Concept(content, implementation, self, conceptIdentity)
    
    def getRawConceptFromIdentity(self, conceptIdentity):
        """
        Returns a Concept object that is in the "raw" state if the ConceptImplementation of the ConceptIdentity object has not yet any loaded Concepts.
        Otherwise it returns a Concept object with ConceptContent, that is obtained by the contentCreationFunction of the ConceptIdentity object.
        """
        implementation = conceptIdentity.implementation
        conceptByIdentity = self._getImplementationDicts(implementation)[0]
        # If there is already a Concept with this ConceptIdentity, ConceptImplementation and ConceptLogic object, return it.
        if conceptIdentity in conceptByIdentity:
            return conceptByIdentity[conceptIdentity]
        # If there are already anny loaded Concepts with this ConceptImplementation or the ConceptLogic is activated, return a loaded Concept.
        if implementation in self._loadedConcepts or self._activated:
            return self.getConceptFromIdentity(conceptIdentity)
        # Return a new raw Concept object. The Concept constructor adds the Concept to the conceptsByIdentity dict.
        return Concept(None, implementation, self, conceptIdentity, True)
    
    def exportSemanticData(self, concepts, nameConvention = None):
        """
        Returns a SemanticData object that contains the semantic data of the exported Concepts.
        """
        # Create a simple counter as nameConvention function if none is given.
        if nameConvention == None:
            nameConvention = lambda concept, counter = itertools.count(): next(counter)
        # Create necessary data structures.
        referenceByConcept = {} # A dict that maps from a Concept object to a reference.
        byteDataInfoByReference = {} # A dict that maps from a reference to a tuple (conceptImplementation, byteData)
        referenceTriples = set() # A set of tuples (subject, predicate, object) where subject, predicate and object are references.
        conceptsToExport = set(concepts)
        exportedConcepts = set()
        # Create references for all Concepts that are to be exported.
        for concept in conceptsToExport:
            referenceByConcept[concept] = nameConvention(concept)
        # Iterate over all Concepts that are to be exported.
        while conceptsToExport:
            concept = conceptsToExport.pop()
            reference = referenceByConcept[concept]
            # If the ConceptImplementation object has byte representation, create a byteDataInfoByReference entry for the Concept and add it to the exportedConcepts set.
            if concept.implementation.getDataFromContent != None:
                byteDataInfoByReference[reference] = (concept.implementation, concept.implementation.getDataFromContent(concept.content, self))
            # If the ConceptImplementation object has no byte representation, get the semanticConnections of the Concept.
            else:
                semanticConnections = concept.implementation.getConnectionsFromContent(concept.content, self)
                # Iterate over all semanticConnections of the Concept.
                for semanticConnection in semanticConnections:
                    newReferenceTriple = [None, None, None]
                    # Iterate over all elements of the semanticConnection.
                    for i in range(3):
                        element = semanticConnection[i]
                        # If the element is None, set the corresponding newReferenceTriple element to the current reference.
                        if element == None:
                            newReferenceTriple[i] = reference
                        # If the element is a Concept, add it to the conceptsToExport set if it is not already exported and set the corresponding newReferenceTriple element to the reference of the Concept.
                        else:
                            if element in referenceByConcept:
                                newReferenceTriple[i] = referenceByConcept[element]
                            else:
                                newReferenceTriple[i] = nameConvention(element)
                                referenceByConcept[element] = newReferenceTriple[i]
                                conceptsToExport.add(element)
                     # Add the newReferenceTriple to the referenceTriples set.
                    referenceTriples.add(tuple(newReferenceTriple))
            # Add the Concept to the exportedConcepts set.
            exportedConcepts.add(concept)
        return (byteDataInfoByReference, referenceTriples)
    
    def importSemanticData(self, semanticData):
        """
        Returns a dict that maps from all references of successfully loaded Concepts to the loaded Concepts.

        This implementation is not optimized for concepts, that are only defined by (None, predicate, object) triples.
        """
        # Create necessary data structures.
        conceptsByReference = {}
        unimportedReferences = set([reference for triple in semanticData[1] for reference in triple])
        referenceTriples = semanticData[1]
        referenceTriplesBySubjectReference = {reference: [triple for triple in referenceTriples if triple[0] == reference] for reference in unimportedReferences}
        referenceTriplesByPredicateReference = {reference: [triple for triple in referenceTriples if triple[1] == reference] for reference in unimportedReferences}
        referenceTriplesByObjectReference = {reference: [triple for triple in referenceTriples if triple[2] == reference] for reference in unimportedReferences}
        untestedReferences = set()
        # Import all Concepts that have byte representation.
        for reference, (conceptImplementation, byteData) in semanticData[0].items():
            conceptsByReference[reference] = self.getConceptFromData(conceptImplementation, byteData)
            if reference in unimportedReferences:
                unimportedReferences.remove(reference)
        # Iterate over all untested references and try to import the Concepts.
        untestedReferences.update(unimportedReferences)
        while untestedReferences:
            reference = untestedReferences.pop()
            # Get the semanticConnections of the reference.
            semanticConnectionReferences = set()
            semanticConnectionReferences.update([(None, triple[1], triple[2]) for triple in referenceTriplesBySubjectReference[reference]])
            semanticConnectionReferences.update([(triple[0], None, triple[2]) for triple in referenceTriplesByPredicateReference[reference]])
            semanticConnectionReferences.update([(triple[0], triple[1], None) for triple in referenceTriplesByObjectReference[reference]])
            semanticConnections = frozenset([
                (conceptsByReference[sub] if sub != None else None, conceptsByReference[pred] if pred != None else None, conceptsByReference[obj] if obj != None else None)
                for sub, pred, obj in semanticConnectionReferences
                if (sub == None or sub in conceptsByReference) and (pred == None or pred in conceptsByReference) and (obj == None or obj in conceptsByReference) 
            ])
            # Try to import the Concept.
            try:
                concept = self.getConceptFromSemanticConnections(semanticConnections)
                conceptsByReference[reference] = concept
                unimportedReferences.remove(reference)
                # Put all connected references back into the untestedReferences set.
                connectedReferences = set([reference for triple in semanticConnectionReferences for reference in triple if reference != None and reference in unimportedReferences])
                untestedReferences.update(connectedReferences)
            except semanticConnectionsNotSufficient:
                pass
        return conceptsByReference
    
    def activate(self):
        """
        Loads all raw Concepts and makes sure that all Concepts are initialized.
        """
        if self._activated:
            return
        for conceptImplementation, conceptsByIdentity in self._identifiedConcepts.items():
            for conceptIdentity, concept in conceptsByIdentity.items():
                if concept.raw:
                    self.getConceptFromIdentity(conceptIdentity)
        self._activated = True

    def getLoadedConcepts(self):
        """
        Returns a set of all currently loaded Concepts.
        """
        return set([concept for conceptsByContent in self._loadedConcepts.values() for concept in conceptsByContent.values()])

class Concept:
    """
    A Concept object is the atomic semantic unit of a ConceptLogic object.
    Every Concept object has a ConceptContent object, a ConceptImplementation object and a ConceptLogic object.
    A Concept object can have a ConceptIdentity object, that is used to identify the Concept across ConceptLogic objects.
    A Concept can be in a "raw" state, where the ConceptContent is not yet defined. This is only allowed for Concepts that have a ConceptIdentity object.
    The initializeConcept function is called if the Concept is initialized.
    The onCall attribute defines the function that is called if the Concept object is called.
    For each attempted acess of an unknown attribute the result of the getConceptAttribute function of the ConceptImplementation object is returned if it is not None.
    If the concept gets called, the callConcept function of the ConceptImplementation object is called if it is not None.
    When there is an attempt to call the concept, access the content or access an unknown attribute of a Concept object that is in a "raw" state, the Concept object is initialized first.
    """
    def __init__(self, content, conceptImplementation, conceptLogic, conceptIdentity = None, raw = False):
        self._conceptImplementation = conceptImplementation
        self._conceptLogic = conceptLogic
        self._conceptIdentity = conceptIdentity
        self._content = content
        self._raw = raw
        if conceptIdentity != None:
            conceptByIdentity = self._conceptLogic._identifiedConcepts[self._conceptImplementation]
            if conceptIdentity in conceptByIdentity:
                raise Exception("There is already a loaded Concept with the same ConceptIdentity object.")
            conceptByIdentity[self._conceptIdentity] = self
        if raw:
            if conceptIdentity == None:
                raise Exception("A Concept object can only be in a raw state if it has a ConceptIdentity object.")
            self._content = None
        else:
            conceptByContent = self._conceptLogic._loadedConcepts[self._conceptImplementation]
            if content in conceptByContent:
                raise Exception("There is already a loaded Concept with the same ConceptContent object.")
            conceptByContent[self._content] = self
            # Initialize the Concept object if the ConceptImplementation object has an initializeConcept function.
            if conceptImplementation.initializeConcept != None:
                conceptImplementation.initializeConcept(self)

    @property
    def implementation(self):
        """
        The ConceptImplementation object of the Concept object.
        """
        return self._conceptImplementation
    
    @property
    def conceptLogic(self):
        """
        The ConceptLogic object of the Concept object.
        """
        return self._conceptLogic
    
    @property
    def identity(self):
        """
        The ConceptIdentity object of the Concept object.
        """
        return self._conceptIdentity
    
    @property
    def content(self):
        """
        The ConceptContent object of the Concept object.
        """
        # If the Concept is in a "raw" state, try to get the ConceptContent object from the ConceptIdentity object.
        if self.raw:
            self._conceptLogic.getConceptFromIdentity(self._conceptIdentity)
        return self._content
    
    @property
    def raw(self):
        """
        A boolean that indicates if the Concept object is in a "raw" state.
        """
        return self._raw
    
    def __oncall__(self):
        """
        Calls the onCall function of the Concept object.
        """
        if self._conceptImplementation.callConcept != None:
            return self._conceptImplementation.callConcept(self)
    
    def __repr__(self):
        """
        Calls the onCall function of the Concept object.
        """
        if self._conceptImplementation.reprConcept != None:
            return self._conceptImplementation.reprConcept(self)
        return "Concept(" + repr(self.content) + ", " + repr(self._conceptImplementation) + ")"
        
    def __getattr__(self, name):
        """
        Returns the value of the attribute with the given name. If the attribute is not yet defined and the Concept is in a "raw" state, the Concept object is initialized.
        """
        if name in self.__dict__:
            return self.__dict__[name]
        if self.raw:
            self._conceptLogic.getConceptFromIdentity(self._conceptIdentity)
        if self._conceptImplementation.getConceptAttribute != None:
            return self._conceptImplementation.getConceptAttribute(self, name)
        raise AttributeError("The Concept object has no attribute " + name + ".")

class ConceptImplementation:
    """
    Base class for ConceptImplementation objects.
    A ConceptImplementation object is a specific way to implement a Concept object.
    It may implement:
        The pair of functions:
            getContentFromData(bytes, conceptLogic) -> ConceptContent
            getDataFromContent(conceptContent, conceptLogic) -> bytes
        The pair of functions:
            getContentFromConnections(connections, conceptLogic) -> ConceptContent
                this may raise an semanticConnectionsNotValid exception or a semanticConnectionsNotSufficient exception
            getConnectionsFromContent(Concept, conceptLogic) -> tuples
        contentValid(ConceptContent, conceptLogic) -> bool
        initializeConcept(Concept) -> None
        implementationSupported(conceptLogic) -> bool
        getConceptAttribute(concept, attributeName) -> object
        callConcept(concept, *args, **kwargs) -> object
    All not implemented functions have to be set to None.
    """
    def __init__(self, getContentFromData = None, getDataFromContent = None,
                 getConnectionsFromContent = None, getContentFromConnections = None, 
                 contentValid = None, initializeConcept = None,
                 implementationSupported = None, getConceptAttribute = None, callConcept = None, reprConcept = None):
        self.getContentFromData = getContentFromData
        self.getDataFromContent = getDataFromContent
        self.getConnectionsFromContent = getConnectionsFromContent
        self.getContentFromConnections = getContentFromConnections
        self.contentValid = contentValid
        self.initializeConcept = initializeConcept
        self.implementationSupported = implementationSupported
        self.getConceptAttribute = getConceptAttribute
        self.callConcept = callConcept
        self.reprConcept = reprConcept
        if (self.getContentFromData == None) != (self.getDataFromContent == None):
            raise Exception("The ConceptImplementation object has to implement either the getContentFromData function and the getDataFromContent function or none of them.")
        if (self.getContentFromConnections == None) != (self.getConnectionsFromContent == None):
            raise Exception("The ConceptImplementation object has to implement either the getContentFromConnections function and the getConnectionsFromContent function or none of them.")
        if self.getContentFromData == None and self.getContentFromConnections == None:
            raise Exception("The ConceptImplementation object has to implement at least one of the functions getContentFromData and getContentFromConnections.")
class semanticConnectionsNotValid(Exception):
    def __init__(self):
        super().__init__("The semantic pairs are not valid.")
"""
    An exception that is raised if the semantic pairs are not valid for creating a ConceptContent object from the ConceptImplementation object.
    """

class semanticConnectionsNotSufficient(Exception):
    def __init__(self):
        super().__init__("The semantic pairs are not sufficient.")
"""
    An exception that is raised if the semantic pairs are not sufficient for creating a ConceptContent object from the ConceptImplementation object.
    """

class ConceptIdentity:
    """
    A ConceptIdentity object is used to identify a Concept across ConceptLogic objects.
    It contains:
        a ConceptImplementation reference, that indicates the ConceptImplementation object that is used to implement the Concept.
        a contentCreationFunction (ConceptLogic) -> ConceptContent, that is used to create the ConceptContent object from the ConceptLogic object. 
    """
    def __init__(self, conceptImplementation, contentCreationFunction):
        self.implementation = conceptImplementation
        self.contentCreationFunction = contentCreationFunction
        # Make sure that there are no loaded Concepts, that implement the conceptImplementation. This could lead to an error if the loaded Concept turns out to be the Concept of this identity.
        global conceptLogicSet
        for conceptLogic in conceptLogicSet:
            if conceptImplementation in conceptLogic.loadedConcepts and conceptLogic.loadedConcepts[conceptImplementation]:
                raise Exception("There is already a loaded Concept for the ConceptImplementation " + str(conceptImplementation) + ".")
            
    def __oncall__(self, conceptLogic):
        """
        Implements a shorthand for getConceptFromIdentity.
        """
        return conceptLogic.getConceptFromIdentity(self)

# ConceptContent
"""
    A ConceptContent is the content of a Concept object.
    It is some hashable data, that is understood by the corresponding ConceptImplementation object.
    """

# SemanticTriple
"""
    A SemanticTriple is a tuple (subject, predicate, object) where subject, predicate and object are Concept objects.
    It indicates that the coresponding statement is true.
    """

# SemanticTriples
"""
    A SemanticTriples object is a set of SemanticTriple objects.
    It represents a set of statements that are true.
    """

# SemanticConnection
"""
    A SemanticConnection object is a tuple (subject, predicate, object) where subject, predicate and object can be eather Concept objects or None values.
    At least one of them has to be a None value.
    The SemanticConnection represents a way how a Concept is connected to it self and other Concepts via a SemanticTriple object.
    The None values mark the places of the target Concept.
    """

# SemanticConections
"""
    A SemanticConnections object is a frozenset of SemanticConnection objects.
    It represents a set of ways how a Concept is connected to it self and other Concepts via SemanticTriple objects.
    """

# SemanticPair
"""
    A SemanticPair object consists of two Concept objects (predicate, object).
    It is used in the context of a specific subject and indicates that the coresponding statement is true.
    """

# SemanticPairs
"""
    A SemanticPairs object is a set of SemanticPair objects.
    It represents a set of statements that are true for a specific subject.
    """

# SemanticData
"""
    A SemanticData object is a tuple (byteDataInfoByReference, referenceTriples) where:
        byteDataInfoByReference is a dict that maps from a reference to a tuple (conceptImplementation, byteData) where:
            conceptImplementation is a ConceptImplementation.
            byteData is a bytes object that is understood by the corresponding ConceptImplementation object.
        referenceTriples is a set of tuples (subject, predicate, object) where subject, predicate and object are references.
        A reference can be any hashable object.
    """

# AbstractSemanticData
"""
    The same as SemanticData but instead of a ConceptImplementation it holds a hashable object representing a ConceptImplementation
    """