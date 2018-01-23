import struct

def pprint(struct):
    class Visitor:
        def __init__(self, identation=0, max_array_elems_per_line=10):
            self.identation = identation;
            self.max_array_elems_per_line = max_array_elems_per_line;
            self.return_text=""

        def visitRawTypeScalar(self, struct, item, meta):
            self.return_text += " "*self.identation
            self.return_text += "{} = {}\n".format(item,struct.__getattr__(item))

        def visitStructuredScalar(self, struct, item, meta):
            self.return_text += " "*self.identation
            self.return_text += "{} = {".format(item, meta)

            inner_visitor = Visitor(self.identation+2,self.max_array_elems_per_line)
            struct.__getattr__(item).accept(inner_visitor)
            self.return_text += inner_visitor.return_text

            self.return_text += " "*self.identation
            self.return_text += "}"

        def visitRawTypeArray(self, struct, item, meta):
            self.return_text += " "*self.identation
            self.return_text += "{}[] = [".format(item)

            a = struct.__getattr__(item)
            element_in_line_idx = 0
            line_idx = 0

            if a.size>self.max_array_elems_per_line:
                self.return_text += "\n"+" "*self.identation

            for v in a.flat:
                if line_idx > 0 and element_in_line_idx == 0:
                    self.return_text += " " * self.identation
                self.return_text += " {}".format(v)
                element_in_line_idx += 1
                if element_in_line_idx > self.max_array_elems_per_line:
                    self.return_text += "\n"
                    line_idx += 1
                    element_in_line_idx=0

            self.return_text += " ]\n"

        def visitStructuredArray(self, struct, item, meta):
            self.return_text += " " * self.identation
            self.return_text += "{}[] = [".format(item)

            a = struct.__getattr__(item)
            for v in a.flat:
                self.return_text += " " * (self.identation+2) + "{\n"
                inner_visitor = Visitor(self.identation + 4, self.max_array_elems_per_line)
                v.accept(inner_visitor)
                self.return_text += inner_visitor.return_text
                self.return_text += " " * (self.identation+2) + "}\n"
            self.return_text += " " * self.identation + "]\n"

    inner_visitor = Visitor(2)
    struct.accept(inner_visitor)
    return "{} {{\n{}}}\n".format(type(struct).__name__,inner_visitor.return_text)
