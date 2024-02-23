"""
This module combines the different components of the StandardLogic implementation and imports them in the right order.
All the components are imported into the global namespace of this module.
Because the different components are refering to each other, the order of the imports is important.
They can refer to each other by using the StandardNamespace object which is defined in the .standardLogicCore module.
The StandardNamespace object provides access to the globals dictionary of this module.
"""

"""
The .standardLogic module defines the StandardNamespace object, which is a WrappedDict that provides access to the globals dictionary of this module.
Therefor the dict attribute of the StandardNamespace object has to be set to the globals dictionary of this module.
The .standardLogic module also defines the StandardLogic class, which is a ConceptLogic that defines the evaluateTripleFunction and the getConceptImplementationFromSemanticConnectionsFunction.
Both functions forward to functionConcepts that get defined at a later stage. They call them by using the StandardNamespace object.
"""
from .standardLogic import StandardNamespace
StandardNamespace.dict = globals()

"""
The .mixedConceptReference module defines the ConceptGetter class, which is a callable that returns a concept for a given ConceptLogic.
It also defines the ensureConcept function, which takes a MixedConceptReference and a ConceptLogic and returns a concept.
"""
from .standardTools import ensureConcept

"""
The .standardConceptImplementation module defines the StandardConceptImplementation class, which is a ConceptImplementation that has an uuid assigned to it.
The uuid is generated from the name and version of the StandardConceptImplementation and is used to identify the StandardConceptImplementation.
This is important for importing and exporting dataConceptClass objects.
"""
from .standardConceptImplementation import StandardLogic, emptyConceptIdentity, CodedConceptClass, DataConceptClass, ConstructedConceptClass, isInstanceOf, getConceptClass, hasConceptClass

"""
The .basicDataConcepts module defines multiple basic DataConceptImplementations.
"""
from .basicDataConcepts import NumberConcept, UUIDConcept, StringConcept

"""
The .basicConstructedConcepts module defines multiple basic ConstructedConceptClassIdentities
"""
from .basicConstructedConcepts import SetConcept, ConnectionConcept, ConnectionsConcept #listConcept

"""
The .basicAbstractions module defines multiple basic ConstructedConceptClassIdentities for Abstract concepts
"""
from .basicAbstractions import DirectAbstraction

"""
The .codedFunctionConcept module defines the codedFunctionConceptIdentity class, which is a ConceptIdentity that wraps python functions so that they can be used as a ConceptIdentity for codedFunctionConcepts.
"""
from .codedFunctionConcept import * #codedFunctionConceptIdentity, codedFunctionConcept, FunctionConceptDecorator

#"""
#The .constructedConceptClass module
#"""

#"""
#The .coreFunctions module defines the evaluateTripleFunction and the getConceptImplementationFromSemanticConnectionsFunction which are the core functions of the StandardLogic implementation.
#"""
#from .coreFunctions import evaluateTripleFunction, getConceptImplementationFromSemanticConnectionsFunction



    