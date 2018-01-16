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
            print("0SET VALUE {}".format(item))
            if item in self.__dict__.keys():
                self.__dict__[item].__set__( self, new_value )
            else:
                raise Exception("unexpected: no attribute {} in {}".format(item, type(self)))


class AttributeBase(object):
    def __init__(self):
        pass

class ScalarAttributeBase(object):
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

    def __set__(self, instance, new_value):
        if self._read_only:
            raise Exception("illegal acces to read only attribute")
        else:
            self._set_value(new_value)

    #    def __get__(self, instance, owner):
#        print("FINAL GETTER getting value {}".format(self.__dict__["_value"]))
#        return self.__dict__["_value"]

    def __delattr__(self, item, _):
        raise Exception("illegal acces to read only attribute")

    def __getattribute__(self, item):
        ret = super(ReadOnlyAttribute, self).__getattribute__(item)
        if not item.startswith("_"):
            print("GET {}".format(item))
            if isinstance(ret, ScalarAttributeBase):
                ret = ret._value
        return ret

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


    def __setattr__(self, item, new_value):
        if self._read_only:
            raise Exception("illegal acces to read only attribute")
        else:
            if item in self._value.__dict__.keys():
                self._value.__dict__[item] = new_value
            else:
                raise Exception("unexpected: no attribute {} in {}".format(item, type(self._value)))

class Attribute(ReadOnlyAttribute):
    def __init__(self, dtype, value):
        super(Attribute,self).__init__(dtype, value, False)

class DynamicArrayAttribute(AttributeBase):
    def __init__(self, dtype, dimensions, read_only=False):
        self.__dict__["_dtype"] = dtype
        self.__dict__["_dimensions"]=dimensions
        self.__dict__["_read_only"] = read_only
        self.adjust_size()

    def _activate_read_only(self):
        self.__dict__["_read_only"]=True

    def adjust_size(self):
        shape = list(map(lambda x:x(), self._dimensions))
        self._value = np.array( shape, dtype = self._dtype )

    def __get__(self, instance, owner):
        return self._value

#    def __getattr__(self, item):
#        return self._value[item]