# Custom interface definition language

This is an example of custom interface definition language.
An example model is given in the file "example.myidl" and "types.myidl".

## Rough outline

### Requirements

1. Items are composed of scalar and array attributes.
1. An attribute type is either a raw type (like an integer) or an item type.
1. A raw type can be mapped to language specific types (e.g., C++ types).
1. Array attributes can have one or more dimensions.
1. Array dimensions are either fixed or depend on other scalar attributes.
1. Array sizes and scalar attributes used to determine their size must be synchronized at all times (invariant).
1. Meta information, such as min/max values, must be provided for each attribute.
1. Iteration over attributes must be supported in a generic way, in order to support textual and binary serialization.


### Generated C++ Code

1. Attributes are represented as public instances of an attribute wrapper.
   * This wrapper contain the data itself and implicit conversions to make its usage as simple as possible: the goal is to make data access feel like a POD attribute access.
   * The wrapper declares its container as friend to grant its owner potentially more access rights than during an external access.
1. Scalar attributes utilized to determine array sizes must be protected from uncontrolled modification.
   * a special read only attribute wrapper represents such attribute.
   * An init function is provided to allow to set scalar attributes utilized to determine array sizes.
1. Array sizes support formulas with integers, scalar attributes of the current item or scalar attributes of items included as scalar attributes of the current item (depth 3, e.g., header.part1.n).
1. Meta information about attributes and structures are provided as compile time information (template arguments and/or constexpr expressions and functions)



## Use the code generator

Get help:
        $ python custom_idl_cpptool.py --help


Run code generation for C++:

        $ python custom_idl_cpptool.py example.myidl --generate-cpp --src-gen-folder=~/Documents/target_folder_for_code

