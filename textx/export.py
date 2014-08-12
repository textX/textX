
def metamodel_export(meta_model, file_name):
    processed_set = set()

    header = '''
        digraph xtext {
        fontname = "Bitstream Vera Sans"
        fontsize = 8
        node[
            shape=record,
            style=filled,
            fillcolor=gold
        ]
        edge[dir=black,arrowtail=empty]


    '''

    with open(file_name, 'w') as f:
        f.write(header)

        for name, m in meta_model.items():
            attrs = ""
            for attr_name, attr_type in m.attrib_types.items():
                # Check if reference
                reference = False
                for ref in m.refs:
                    if ref[0] == attr_name:
                        reference = True
                        break
                for cont in m.cont:
                    if cont[0] == attr_name:
                        reference = True
                        break
                if not reference:
                    if attr_type is not None:
                        attrs += "+{}:{}\\l".format(attr_name, attr_type)
                    else:
                        attrs += "+{}\\l".format(attr_name)

            inheritance = ""
            for inherited_by in m.inh_by:
                inheritance += '{} -> {} [dir=back]\n'.format(name, inherited_by.__name__)

            containments = ""
            for cont in m.cont:
                attr_name, metacls, mult = cont
                containments += '{} -> {}[arrowtail=diamond, arrowhead=normal, dir=both, headlabel="{} {}"]\n'\
                        .format(name, metacls.__name__, attr_name, '')

            references = ""
            for ref in m.refs:
                attr_name, metacls, mult = ref
                references += '{} -> {}[arrowhead=normal, dir=both, headlabel="{} {}"]\n'\
                        .format(name, metacls.__name__, attr_name, mult)

            f.write('{}[ label="{{{}|{}}}"]\n'.format(\
                    name, name, attrs))
            f.write(inheritance)
            f.write(containments)
            f.write(references)
            f.write("\n")


        f.write("\n}\n")


def model_export(model, file_name):

    header = '''
        digraph xtext {
        size="5,5"
        node[shape=record,style=filled,fillcolor=gray95]
        edge[dir=black,arrowtail=empty]

    '''

    with open(file_name, 'w') as f:
        f.write(header)

        def _export(m):

            # Get primitive attributes
            attrib = ""
            name = m.__class__.__name__
            for attr in m.__dict__:
                if attr=='name':
                    name = getattr(m, attr)
                elif type(attr) in [bool, int, float, str]:
                    attr+="+{}\\".format(str(getattr(m, attr)))
            f.write('{}[label="{}|{}"]\n'.format(id(m), name, attr))

        _export(model)

        f.write('\n}\n')


