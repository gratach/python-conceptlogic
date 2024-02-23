from .codedFunctionConcept import FunctionConceptDecorator

@FunctionConceptDecorator
def evaluateTriples(conceptLogic, semanticTripleAbstraction):
    """
    FunctionConcept that takes the abstraction of a conceptList with tree entries as argument and returns the abstraction of a truth value
    """
    pass
    # Check if the semanticTripleAbstraction can be seperated into a subject-, predicate- and objectAbstraction. This applies in the following cases:
        # The semanticTripleAbstraction is a directAbstraction of a listConcept with three elements.
        # The getKownFundamentalSemanticConnections function returns the signature of a listConcept with three elements.
    # If this is the case, check if the getPredicateEvaluationFunction function returns a function for the predicateAbstraction.
        # If this is the case, call the function with the subjectAbstraction and the objectAbstraction as abstract triple argument and return the result.
    ### Some other cases
    # Return the trivial answer that the triple is true if the triple is true.

@FunctionConceptDecorator
def getConceptImplementationFromSemanticConnections(conceptLogic, semanticConnectionsAbstraction):
    """
    FunctionConcept that takes the abstraction of a semanticConnections concept as argument and returns the abstraction of a conceptImplementation.
        A semanticConnections concept is a listConcept with an arbitrary number of semanticConnections as elements.
            A semanticConnection is a listConcept with three maybeConcepts as elements.
                A maybeConcept is an optional reference to a concept.
    """
    pass
    # Check if the semanticConnectionsAbstraction can be seperated into a list of semanticConnectionAbstractions.
        # If this is the case, check if any of the semanticConnectionAbstractions can be seperated into a list of three maybeConceptAbstractions,
        # where the first one is a directAbstraction of empty maybeConcept, the second one is a directAbstraction of a maybeConcept pointing to an isInstanceOf concept
        # and the third one is a directAbstraction of a maybeConcept pointing to a conceptClass.
            # If this is the case:
            # Check if the conceptClass is a dataConceptClass.
                # If this is the case, return the conceptImplementation of the dataConceptClass.
            # Check if the conceptClass is a constructedConceptClass.
                # If this is the case, call the getConceptImplementationFromSemanticConnections function of the constructedConceptClass
                # with the remaining unpackable semanticConnectionAbstractions as arguments and return the result.

@FunctionConceptDecorator
def getFundamentalSemanticConnections(conceptLogic, abstraction):
    """
    FunctionConcept that takes the abstraction of a concept as argument and returns the abstraction of a listConcept with semanticConnections as elements.
    The return value represents the fundamentalSemanticConnections of the concept.
    """
    pass
    # Check if the abstraction is a directAbstraction of a concept.
        # If this is the case, check if the concepts implementation has a getSematicConnectionsFromContent function.
            # If this is the case, return the abstract version of the result of this function.

@FunctionConceptDecorator
def getPredicateEvaluationFunction(conceptLogic, predicateAbstraction):
    pass

@FunctionConceptDecorator
def isEqual(conceptLogic, abstraction1, abstraction2):
    """
    FunctionConcept that takes two abstractions as arguments and returns the abstraction of a truth value.
    """
    pass
    # Check if the abstractions are directAbstractions of concepts.
        # If this is the case, return the directAbstraction of the truth value of the equality of the concepts.

@FunctionConceptDecorator
def getInterfaceRealization(conceptLogic, targetAbstraction, interfaceAbstraction):
    """
    FunctionConcept that takes an abstraction of a target concept and an abstraction of an interface concept as arguments and returns 
    the abstraction of the target concepts interfaceRealization of the interface concept.
    """
    pass
    # Get the fundamentalSemanticConnections of the interfaceAbstraction by calling the getFundamentalSemanticConnections function.
    # Check if the result contains a triple ( - , hasExplicitInterfaceRealizationFinderByClass, <interfaceRealizationFinderByClass> ).
    # Get the fundamentalSemanticConnections of the targetAbstraction by calling the getFundamentalSemanticConnections function.
    # Check if the result contains a triple ( - , isInstanceOf, <conceptClass> ).
        # If this is the case, do for the class and all superclasses:
            # If the class is a key of the interfaceRealizationFinderByClass dictionary, call the interfaceRealizationFinderByClass value function with the targetAbstraction as argument and return the result.
            # Check if the fundamentalSemanticConnentions of the class contains a triple ( - , hasInterfaceRealizationFinderByInterface, <interfaceRealizationFinderByInterface> ).
                # If this is the case, check if the concept of the interfaceAbstraction is a key of the interfaceRealizationFinderByInterface dictionary.
                    # If this is the case, call the interfaceRealizationFinderByInterface value function with the targetAbstraction as argument and return the result.
            # Check if the fundamentalSemanticConnentions of the class contains triples ( - , hasSuperClass, <superClass> ).
                # If this is the case, repeat the process for every <superClass> that was not already used.
    