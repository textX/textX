from __future__ import absolute_import
from __future__ import unicode_literals
from os.path import dirname, exists
from shutil import rmtree
import os.path
from pytest import raises
import importlib
import numpy as np

class add_path:
    def __init__(self):
        pass

    def __enter__(self):
        """
        add example code to path
        """
        import sys
        self.this_folder = os.path.dirname(__file__)
        folders = os.path.split(os.path.abspath(self.this_folder))
        example_name = folders[-1]
        self.example_dir = os.path.abspath(os.path.join(folders[0], "../../../examples/" + example_name))
        sys.path.insert(0, self.example_dir)
        sys.path.insert(0, self.this_folder)
        print("added {} and {}".format(self.example_dir, self.this_folder))

    def __exit__(self, exc_type, exc_value, traceback):
        import sys
        sys.path.remove(self.example_dir)
        sys.path.remove(self.this_folder)
        print("removed {} and {}".format(self.example_dir, self.this_folder))


def test_basic_python_code():

    with add_path():
        import custom_idl_codegen as codegen

        #################################
        # Model definition and Code creation
        #################################

        this_folder = dirname(__file__)
        # cleanup old generated code
        if exists(os.path.join(this_folder,"mypackage1")):
            rmtree(os.path.join(this_folder, "attributes"))
            rmtree(os.path.join(this_folder,"mypackage1"))
        # check that no old generated code is present
        assert not exists(os.path.join(this_folder,"mypackage1/test/Header.py"))
        assert not exists(os.path.join(this_folder,"mypackage1/test/Data.py"))
        assert not exists(os.path.join(this_folder,"mypackage1/test/Simple.py"))

        codegen.codegen(srcgen_folder=this_folder,
                        generate_python=True,
                        model_string=
"""
// model
package types {
    type int    {   python: "int" with format "i" }
    type float  {   python: "float" with format "f" }
    type UINT8  {   python: "uint8"  from 'numpy' with format "B" }
    type UINT16 {   python: "uint16" from 'numpy' with format "H" }
}
package mypackage1 {
    target_namespace "mypackage1.test"
    struct Header {
        scalar proofword : types.int
        scalar N : types.int { default = "0x16" }
        scalar k : types.int
        array info : types.float[10]
    }
    struct Data {
        scalar header   : Header
        scalar n        : types.int {default="5"}
        scalar x_f      : types.float
        scalar x_i      : types.int
        scalar x_ui16   : types.UINT16
        array  a_ui16   : types.UINT16
                            [header.N:master_index]
                            [n:client_index]
                            [2:real_imag]
        array  a_f      : types.float
                            [header.N:master_index]
                            [n:client_index]
        array  headers  : Header
                            [header.N:master_index]
                            [n:client_index]
    }
    struct Simple {
        scalar n        : types.UINT16 {default="5"}
        scalar x        : types.UINT16
        array  a_ui16   : types.UINT16[n]
    }
}
""")

        #################################
        # Using the model classes
        #################################

        # have the classes been created?
        assert exists(os.path.join(this_folder,"mypackage1/test/Header.py"))
        assert exists(os.path.join(this_folder,"mypackage1/test/Data.py"))
        assert exists(os.path.join(this_folder,"mypackage1/test/Simple.py"))

        #use them:
        HeaderLib = importlib.import_module("mypackage1.test.Header")
        DataLib   = importlib.import_module("mypackage1.test.Data")
        SimpleLib = importlib.import_module("mypackage1.test.Simple")
        toolLib = importlib.import_module("attributes.tools")

        header = HeaderLib.Header()
        data = DataLib.Data()

        # alloed acces
        header.N = 11

        # disallowd acces (size controlling attribute)
        with raises(Exception, match=r'.*illegal access.*read only.*'):
            data.header.N = 12

        # set size (multiple times)
        data.init(header, 33)
        assert data.a_ui16.shape == (11,33,2)
        header.N = 13
        data.init(header, 33)
        # check also linked sizes (more than one array with correlated sizes)
        assert data.a_ui16.shape == (13,33,2)
        assert data.a_f.shape == (13,33)
        assert data.headers.shape == (13,33)

        simple = SimpleLib.Simple()
        simple.init(3)
        assert simple.a_ui16.shape == (3,)
        simple.a_ui16 = np.linspace(0,90,3, dtype=np.uint16)

        simple_as_text = toolLib.pprint(simple)
        assert simple_as_text == \
"""Simple {
  n = 3
  x = 0
  a_ui16[] = [ 0 45 90 ]
}
"""
        #x.byteswap().tobytes()

        #################################
        # END
        #################################

        rmtree(os.path.join(this_folder,"mypackage1"))
        rmtree(os.path.join(this_folder,"attributes"))
        assert not exists(os.path.join(this_folder,"mypackage1/test/Header.py"))
        assert not exists(os.path.join(this_folder,"mypackage1/test/Data.py"))
        assert not exists(os.path.join(this_folder,"mypackage1/test/Simple.py"))
