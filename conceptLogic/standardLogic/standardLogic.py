
from ..conceptLogic.conceptLogic import ConceptLogic, ConceptIdentity

class WrappedDict:
    """
    A wrapped dictionary whose values can be accessed as attributes.
    The dict attribute is the dictionary that is wrapped.
    """
    def __init__(self, dictarg = {}):
        self.dict = dictarg
    def __getattr__(self, name):
        if name == "dict":
            return self.__dict__["dict"]
        if hasattr(self.dict, name):
            return getattr(self.dict, name)
        if name in self.dict:
            return self.dict[name]
        raise AttributeError("WrappedDict has no attribute '{}'".format(name))
    def __setattr__(self, name, value):
        if name == "dict":
            self.__dict__["dict"] = value
        else:
            self.dict[name] = value
    def __getitem__(self, key):
        return self.dict[key]
    def __setitem__(self, key, value):
        self.dict[key] = value


StandardNamespace = sn = WrappedDict()