import uuid
import inspect
from .standardTools import ensureConcept
from ..conceptLogic.conceptLogic import ConceptIdentity
# TODO from .basicConstructedConcepts import listConcept
from .standardConceptImplementation import CodedConceptClass, ConceptMethode

_codedFunctionConceptIdentitiesByUUID = {}
_codedFunctionConceptIdentitiesByFunction = {}
_CodeFunctionNamespaceUUID = uuid.uuid3(uuid.NAMESPACE_DNS, "CodeFunctionNamespaceUUID")
class codedFunctionConceptIdentity(ConceptIdentity):
    """
    Instances of this class wrap python functions so that they can be used as a ConceptIdentity for codedFunctionConcepts.
    The python function has to take the conceptLogic as first argument and at least one concept as the remaining arguments.
    If the python function takes more than one concept as argument, the resulting codedFunctionConcept will take a conceptList of concepts as arguments that will be unpacked and passed to the python function.
    The constructor arguments are:
        function: The python function that is wrapped by this codedFunctionConceptIdentity.
        argumentConceptCategory:
            If the python function takes one concept argument, this is a mixedConceptReference to the ConceptCategory of the concept argument.
            If the python function takes more than one concept argument, this is a tuple of mixedConceptReferences to the ConceptCategories of the concept arguments.
        returnConceptCategory: A mixedConceptReference to the ConceptCategory of the return value of the python function.
        and optionally:
            version: The version of the python function.
    """
    def __init__(self, function, argumentConceptCategory, returnConceptCategory, version = "0.0.0"):
        # Generate a UUID for this instance
        self.uuid = uuid.uuid3(_CodeFunctionNamespaceUUID, function.__name__ + " " + version).bytes
        # Check if there is already a codedFunctionConceptIdentity with this uuid
        if self.uuid in _codedFunctionConceptIdentitiesByUUID:
            raise Exception("There is already a codedFunctionConceptIdentity with this uuid.")
        # Check if there is already a codedFunctionConceptIdentity with this function
        if function in _codedFunctionConceptIdentitiesByFunction:
            raise Exception("There is already a codedFunctionConceptIdentity with this function.")
        # Check if the type of the argumentConceptCategory is compatible with the number of arguments of the function
        self._argumentNumber = len(inspect.getfullargspec(function).args) - 1
        if type(argumentConceptCategory) in [tuple, list]:
            if len(argumentConceptCategory) != self._argumentNumber:
                raise Exception("The length of the argumentConceptCategory does not match the number of arguments of the function.")
        else:
            if len(inspect.getfullargspec(function).args) != 1:
                raise Exception("The function does not take exactly one argument.")
        # Add the unused conceptCategories
        self._unusedArgumentConceptCategory = argumentConceptCategory
        self._unusedReturnConceptCategory = returnConceptCategory
        self.argumentConceptCategory = None
        self.returnConceptCategory = None
        # Add this instance to the dictionary
        _codedFunctionConceptIdentitiesByUUID[self.uuid] = self
        _codedFunctionConceptIdentitiesByFunction[function] = self
        # Initialize the ConceptIdentity
        super().__init__(codedFunctionConcept, lambda conceptLogic: self)
        self.function = function

    def callUnsafe(self, conceptLogic, *arguments):
        """
        This function calls the python function with the given arguments without checking the conceptCategories or converting the arguments to match it.
        It converts the arguments into concepts and unpacks them if necessary.
        """
        arguments = [ensureConcept(argument, conceptLogic) for argument in arguments]
        if len(arguments) == 1:
            argument = arguments[0]
            if self._argumentNumber == 1:
                return self.function(conceptLogic, argument)
            # TODO check / reimplement
            #if not argument.implementation == listConcept:
            #    raise Exception("The argument is not a conceptList.")
            if len(argument.content) != self._argumentNumber:
                raise Exception("The length of the argument does not match the number of arguments of the function.")
            return self.function(conceptLogic, *argument.content)
        if len(arguments) == self._argumentNumber:
            return self.function(conceptLogic, *arguments)
        raise Exception("The number of arguments does not match the number of arguments of the function.")
            

    
class codedFunctionConcept(metaclass=CodedConceptClass):
    """
    A CodedConceptIdentity that implements CodedFunctionConcepts (concepts representing python functions that take a fixed number of concepts as arguments and return a concept).
    It uses codedFunctionIdentity objects as ConceptContent.
    """
    def getContentFromData(data, conceptLogic):
        return _codedFunctionConceptIdentitiesByUUID[uuid.UUID(data.decode("utf-8"))]

    def getDataFromContent(content, conceptLogic):
        return str(content.uuid).encode("utf-8")

    def contentValid(content, conceptLogic):
        return content in _codedFunctionConceptIdentitiesByUUID.values()
    
    @ConceptMethode
    def callUnsafe(content, conceptLogic, *arguments):
        return content.callUnsafe(conceptLogic, *arguments)
    
class FunctionConceptDecorator:
    """
    This decorator converts python functions into codedFunctionConcepts.
    The decorator can be used in two ways:
        1) @FunctionConceptDecorator
            def function(conceptLogic, ...):
                ...
        2) @FunctionConceptDecorator(argumentConceptCategory, returnConceptCategory)
            def function(conceptLogic, ...):
                ...
    """
    def __new__(cls, *args):
        """
        This function is called when the decorator is used.
        """
        # If the decorator is used with one argument, the argument is the function that is decorated
        if len(args) == 1 and callable(args[0]):
            return codedFunctionConceptIdentity(args[0], None, None)
        # If the decorator is used with two arguments, the first argument is the argumentConceptCategory and the second argument is the returnConceptCategory
        if len(args) == 2:
            return object.__new__(cls)
        else:
            raise Exception("Invalid number of arguments.")
    def __init__(self, argumentConceptCategory, returnConceptCategory):
        """
        This function is called when the decorator is used with two arguments.
        """
        self.argumentConceptCategory = argumentConceptCategory
        self.returnConceptCategory = returnConceptCategory
    def __call__(self, function):
        """
        This function is called when the decorator is used with two arguments.
        """
        return codedFunctionConceptIdentity(function, self.argumentConceptCategory, self.returnConceptCategory)


