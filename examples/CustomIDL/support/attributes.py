import numpy as np
from copy import copy

class BaseStruct(object):
    def __init__(self, read_only=False):
        self.__dict__["_read_only"]=read_only

    def __getattribute__(self, item):
        ret = super(BaseStruct,self).__getattribute__(item)
        if not item.startswith("_"):
            print("0GET {}".format(item))
            if isinstance(ret, ScalarAttributeBase):
                ret = ret._value
            elif isinstance(ret, ArrayAttributeBase):
                ret = ret._get_view()
        return ret

    def _activate_read_only(self):
        self.__dict__["_read_only"]=True
        for key in self.__dict__:
            if not key.startswith("_"):
                if isinstance(self.__dict__[key], AttributeBase):
                    self.__dict__[key]._activate_read_only()


    def _set_value(self, item, new_value):
        print("internal 0SET VALUE {}".format(item))
        if item in self.__dict__.keys():
            self.__dict__[item]._set_value( new_value )
        else:
            raise Exception("unexpected: no attribute {} in {}".format(item, type(self)))

    def __setattr__(self, item, new_value):
        if self._read_only:
            raise Exception("illegal acces to read only attribute")
        else:
            self._set_value(item, new_value)


class AttributeBase(object):
    def __init__(self):
        pass

class ScalarAttributeBase(object):
    def __init__(self):
        pass

class ArrayAttributeBase(object):
    def __init__(self):
        pass

class ReadOnlyAttribute(ScalarAttributeBase):
    def __init__(self, dtype, value, read_only=True):
        self.__dict__["_dtype"] = dtype
        self.__dict__["_value"] = value
        self.__dict__["_read_only"] = False
        if read_only:
            self._activate_read_only()

    def _activate_read_only(self):
        self.__dict__["_read_only"]=True
        if isinstance(self._value, BaseStruct):
            self._value._activate_read_only()

    def _set_value(self, new_value):
        if type(new_value) is type(self._value):
            print("SETTER setting value {}".format(new_value))
            if isinstance(self._value, BaseStruct) and self._value._read_only:
                self.__dict__["_value"] = copy(new_value)
                self.__dict__["_value"]._activate_read_only()
            else:
                self.__dict__["_value"] = copy(new_value)
        else:
            raise Exception("unexpected type {} for {}".format(type(new_value), type(self._value)))

    def __set__(self, instance , new_value):
        if self._read_only:
            raise Exception("illegal acces to read only attribute")
        else:
            self._set_value(new_value)


class Attribute(ReadOnlyAttribute):
    def __init__(self, dtype, value):
        super(Attribute,self).__init__(dtype, value, False)


class DynamicArrayAttribute(ArrayAttributeBase):
    def __init__(self, dtype, dimensions, read_only=False):
        self.__dict__["_dtype"] = dtype
        self.__dict__["_dimensions"]=dimensions
        self.__dict__["_read_only"] = read_only
        self._adjust_size()

    def _activate_read_only(self):
        self.__dict__["_read_only"]=True
        if issubclass(self._dtype, BaseStruct): # TODO: TEST
            for x in self._value:
                x._activate_read_only();

    def _adjust_size(self):
        shape = list(map(lambda x:x(), self._dimensions))
        self.__dict__["_value"] = np.empty( shape, dtype = self._dtype )

    def _get_view(self):
        return self._value.view()
