import numpy as np

class ReadOnlyAttribute:
    def __init__(self, dtype=int, value=dtype()):
        self._dtype = dtype
        self._value = value

    def __get__(self, instance, owner):
        return self._value


class Attribute(ReadOnlyAttribute):
    def __init__(self, dtype=int, value=dtype()):
        super(ReadOnlyAttribute,self).__init__(dtype, value)

    def __set__(self, instance, value):
        return self._value = value


class DynamicArrayAttribute:
    def __init__(self, dimensions, dtype=int):
        self._dtype = dtype
        self._dimensions=dimensions
        self.adjust_size()

    def adjust_size(self):
        shape = map(lambda x:x(), self._dimensions())
        self._value = np.array( shape, dtype = self.dtype )

    def __get__(self, instance, owner):
        return self._value

#    def __getattr__(self, item):
#        return self._value[item]