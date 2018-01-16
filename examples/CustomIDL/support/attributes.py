import numpy as np

class ReadOnlyAttribute(object):
    def __init__(self, dtype, value):
        self.__dict__["_dtype"] = dtype
        self.__dict__["_value"] = value

    def __get__(self, instance, owner):
        return self._value

    def __int__(self):
        return self._value

    def __getattr__(self, item):
        return self._value.__dict__[item].as_read_only_attribute()

    def as_read_only_attribute(self):
        return ReadOnlyAttribute(self._dtype, self._value)


class Attribute(ReadOnlyAttribute):
    def __init__(self, dtype, value):
        super(Attribute,self).__init__(dtype, value)

    def __set__(self, instance, value):
        self._value = value

    def __getattr__(self, item):
        return self._value.__dict__[item]

    def __setattr__(self, item, new_value):
        if item in self._value.__dict__.keys():
            self._value.__dict__[item] = new_value
        else:
            raise Exception("unexpected: no attribute {} in {}".format(item, type(self._value)))

class DynamicArrayAttribute(object):
    def __init__(self, dtype, dimensions):
        self._dtype = dtype
        self._dimensions=dimensions
        self.adjust_size()

    def adjust_size(self):
        shape = list(map(lambda x:x(), self._dimensions))
        self._value = np.array( shape, dtype = self._dtype )

    def __get__(self, instance, owner):
        return self._value

#    def __getattr__(self, item):
#        return self._value[item]