import numpy as np

class ReadOnlyAttribute(object):
    def __init__(self, dtype, value):
        self._dtype = dtype
        self._value = value

    def __get__(self, instance, owner):
        return self._value


class Attribute(ReadOnlyAttribute):
    def __init__(self, dtype, value):
        super(Attribute,self).__init__(dtype, value)

    def __set__(self, instance, value):
        self._value = value


class DynamicArrayAttribute(object):
    def __init__(self, dtype, dimensions):
        self._dtype = dtype
        self._dimensions=dimensions
        self.adjust_size()

    def adjust_size(self):
        shape = map(lambda x:x(), self._dimensions)
        self._value = np.array( shape, dtype = self._dtype )

    def __get__(self, instance, owner):
        return self._value

#    def __getattr__(self, item):
#        return self._value[item]