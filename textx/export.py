
# def meta_model_export(meta_model, file_name):
#     processed_set = set()
#
#     header = '''
#         digraph xtext {
#         size="5,5"
#         node[shape=record,style=filled,fillcolor=gray95]
#         edge[dir=black,arrowtail=empty]
#
#
#     '''
#
#     with open(file_name, 'w') as f:
#         f.write(header)
#
#         for m in meta_model
#


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
            f.write('{}[label="{}|{}]"'.format(id(m), name, attr))

        _export(model)

        f.write('\n}\n')


