from __future__ import absolute_import
from __future__ import unicode_literals
import custom_idl_codegen as codegen
from os.path import dirname, exists
from shutil import rmtree
import os.path
from pytest import raises

def add_example_folder_to_path_based_on_local_folder():
    """
    add example code to path
    """
    import sys
    this_folder = os.path.dirname(__file__)
    folders = os.path.split(os.path.abspath(this_folder))
    example_name = folders[-1]
    example_dir = os.path.abspath(os.path.join(folders[0], "../../../examples/" + example_name))
    print(example_dir)
    sys.path.insert(0, example_dir)
    sys.path.insert(0, this_folder)
    print(f"added {example_dir} and {this_folder}")


def test_basic_python_code():

    add_example_folder_to_path_based_on_local_folder()

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
                    generate_cpp=False,
                    generate_python=True,
                    model_string=
"""
// model
package types {
    type int    {   python: "int"}
    type float  {   python: "float" }
    type UINT8  {   python: "uint8"  from 'numpy' }
    type UINT16 {   python: "uint16" from 'numpy' }
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
    from mypackage1.test.Header import Header
    from mypackage1.test.Data import Data
    from mypackage1.test.Simple import Simple

    header = Header()
    data = Data()

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

    simple = Simple()
    simple.init(3)
    assert simple.a_ui16.shape == (3,)

    #x.byteswap().tobytes()

    #################################
    # END
    #################################

    rmtree(os.path.join(this_folder,"mypackage1"))
    rmtree(os.path.join(this_folder,"attributes"))
    assert not exists(os.path.join(this_folder,"mypackage1/test/Header.py"))
    assert not exists(os.path.join(this_folder,"mypackage1/test/Data.py"))
    assert not exists(os.path.join(this_folder,"mypackage1/test/Simple.py"))
