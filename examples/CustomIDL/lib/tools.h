#ifndef _ATTRIBUTES_TOOLS_H
#define _ATTRIBUTES_TOOLS_H

#include <iostream>
#include <string>

namespace attributes {
    namespace tools {

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
        
        /** Pretty prints a structure.
         * @param structure: a structure with attributes
         */
        template<class S>
        void pprint(const S& structure, std::ostream &out = std::cout) {
            using MetaInfo = typename S::MetaInfo;
            out << MetaInfo::type_name() << " {\n";
            Visitor visitor{out,2};
            structure.accept(visitor);
            out << "}\n";
        }
        
        
    }
}

#endif /* _ATTRIBUTES_TOOLS_H */

