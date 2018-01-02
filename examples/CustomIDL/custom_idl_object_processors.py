from textx import model_root

def check_scalar_ref(scalar_ref):
    def myassert(ref):
        assert ref.default_value, "{}: {}.{} needs to have a default value".format(model_root(ref)._tx_filename,ref.parent.name,ref.name)
    if scalar_ref.ref2:
        myassert(scalar_ref.ref2)
    elif scalar_ref.ref1:
        myassert(scalar_ref.ref1)
    else:
        myassert(scalar_ref.ref0)

class CheckRawTypes(object):
    def __init__(self,options):
        if options:
            self.options = options
        else:
            self.options = {}

    def __call__(self, rawtype):
        if "generate_cpp" in self.options.keys() and self.options["generate_cpp"]:
            assert rawtype.cpptype, "C++ type is required to generate C++ code for {} in {}".format(rawtype.name, model_root(rawtype)._tx_filename)

