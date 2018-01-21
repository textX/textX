#ifndef _ATTRIBUTES_TOOLS_H
#define _ATTRIBUTES_TOOLS_H

#include <iostream>
#include <string>

namespace attributes {
    namespace tools {

        namespace pprint_support {
            struct Visitor {
                std::ostream &out;
                size_t identation=0;
                size_t max_array_elems_per_line=10;

                template<class MetaInfo, class Owner, class T>
                void visitRawTypeScalar(const Owner&, const T& value) {
                    out << std::string(identation, ' ') << MetaInfo::type_name() << " " << MetaInfo::name() << " = " << value << "\n";
                }

                template<class MetaInfo, class Owner, class T>
                void visitStructuredScalar(const Owner&, const T& value) {
                    Visitor visitor{out, identation+2,max_array_elems_per_line};
                    out << std::string(identation, ' ') << MetaInfo::type_name() << " " << MetaInfo::name() << " = {\n";
                    value.accept(visitor);
                    out << std::string(identation, ' ') << "}\n";
                }

                template<class MetaInfo, class Owner, class T>
                void visitRawTypeArray(const Owner&, const T& value) {
                    out << std::string(identation, ' ') << MetaInfo::type_name() << "[] " << MetaInfo::name() << " = [";
                    size_t element_in_line_idx=0;
                    size_t line_idx=0;
                    if (value.size()>max_array_elems_per_line) {
                            out << "\n" << std::string(identation, ' ');
                    }
                    for (const auto &v: value) {
                        if (line_idx>0 and element_in_line_idx==0) {
                            out << std::string(identation, ' ');
                        }
                        out << " " << v;
                        element_in_line_idx++;
                        if (element_in_line_idx>max_array_elems_per_line) {
                            out << "\n";
                            line_idx++;
                            element_in_line_idx=0;
                        }
                    }
                    out << " ]\n";
                }

                template<class MetaInfo, class Owner, class T>
                void visitStructuredArray(const Owner&, const T& value) {
                    Visitor visitor{out, identation+4,max_array_elems_per_line};
                    out << std::string(identation, ' ') << MetaInfo::type_name() << "[] " << MetaInfo::name() << " = [";
                    for (const auto &v: value) {
                        out << std::string(" ",identation+2) << "{\n";
                        v.accept(visitor);
                        out << std::string(" ",identation+2) << "}\n";
                    }
                    out << std::string(identation, ' ') << "]\n";
                }
            };
        }

        /** Pretty prints a structure.
         * @param structure: a structure with attributes
         */
        template<class S>
        void pprint(const S& structure, std::ostream &out = std::cout) {
            using MetaInfo = typename S::MetaInfo;
            out << MetaInfo::type_name() << " {\n";
            pprint_support::Visitor visitor{out,2};
            structure.accept(visitor);
            out << "}\n";
        }


        namespace binary_write_support {
            struct Visitor {
                std::ostream &out;

                template<class MetaInfo, class Owner, class T>
                void visitRawTypeScalar(const Owner&, const T& value) {
                    out.write( reinterpret_cast<const char*>( &value ), sizeof( T ) );
                }

                template<class MetaInfo, class Owner, class T>
                void visitStructuredScalar(const Owner&, const T& value) {
                    Visitor visitor{out};
                    value.accept(visitor);
                }

                template<class MetaInfo, class Owner, class T>
                void visitRawTypeArray(const Owner&, const T& value) {
                    for (const auto &v: value) {
                        out.write( reinterpret_cast<const char*>( &v ), sizeof( T ) );
                    }
                }

                template<class MetaInfo, class Owner, class T>
                void visitStructuredArray(const Owner&, const T& value) {
                    Visitor visitor{out};
                    for (const auto &v: value) {
                        v.accept(visitor);
                    }
                }
            };
        }

        /** binary write a structure.
         * @param structure: a structure with attributes
         * @param out: output file
         */
        template<class S>
        void binary_write(const S& structure, std::ostream &out) {
            //using MetaInfo = typename S::MetaInfo;
            binary_write_support::Visitor visitor{out};
            structure.accept(visitor);
        }


        namespace binary_read_support {
            struct Visitor {
                std::istream &inp;

                template<class MetaInfo, class Owner, class T>
                void visitRawTypeScalar(Owner&, T& value) {
                    inp.read( reinterpret_cast<char*>( &value ), sizeof( T ) );
                }

                template<class MetaInfo, class Owner, class T>
                void visitStructuredScalar(Owner&, T& value) {
                    Visitor visitor{inp};
                    value.accept_and_init(visitor);
                }

                template<class MetaInfo, class Owner, class T>
                void visitRawTypeArray(Owner&, T& value) {
                    for (auto &v: value) {
                        inp.read( reinterpret_cast<char*>( &v ), sizeof( T ) );
                    }
                }

                template<class MetaInfo, class Owner, class T>
                void visitStructuredArray(Owner&, T& value) {
                    Visitor visitor{inp};
                    for (auto &v: value) {
                        v.accept_and_init(visitor);
                    }
                }
            };
        }

        /** binary read a structure.
         * @param structure: a structure with attributes
         * @param inp: input file
         */
        template<class S>
        void binary_read(S& structure, std::istream &inp) {
            //using MetaInfo = typename S::MetaInfo;
            binary_read_support::Visitor visitor{inp};
            structure.accept_and_init(visitor);
        }
        
    }
}

#endif /* _ATTRIBUTES_TOOLS_H */

