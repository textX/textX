from __future__ import unicode_literals
from textx import metamodel_from_file
from textx.export import metamodel_export, PlantUmlRenderer
import fnmatch
import os
from os.path import sep, join, dirname, exists


def main(path=None, debug=False):
    if path is None:
        path = join(dirname(__file__), "..", "..")

    print("render_all_grammars.py - example program")
    matches = []
    for root, dirnames, filenames in os.walk(path):
        for filename in fnmatch.filter(filenames, '*.tx'):
            matches.append((root, filename))

    with open("README.md", "wt") as md:
        md.write("# All grammars (*.tx)\n")
        for m in matches:
            inname = join(m[0], m[1])
            outfname_base = "{}_{}".format(
                m[0].replace(path, '').lstrip(sep).replace(sep, '_'),
                m[1].rstrip('.tx'))
            destpath = join(dirname(__file__), "dot")
            if not exists(destpath):
                os.mkdir(destpath)
            dest_dot = join(destpath, outfname_base + ".dot")
            dest_dot_png = join(destpath, outfname_base + ".dot.png")
            destpath = join(dirname(__file__), "pu")
            if not exists(destpath):
                os.mkdir(destpath)
            dest_pu = join(destpath, outfname_base+".pu")
            dest_pu_png = join(destpath, outfname_base+".png")

            print(dest_dot)
            mm = metamodel_from_file(inname, debug=debug)
            metamodel_export(mm, dest_dot)
            metamodel_export(mm, dest_pu, renderer=PlantUmlRenderer())

            md.write("## {}\n".format(m[1]))
            md.write(" * source: {}/{}\n".format(m[0], m[1]))
            md.write(" * basename: {}\n".format(outfname_base))
            md.write('\n')
            md.write('<img width="49%" src="{}" alt="{}">\n'.format(
                dest_pu_png, dest_pu_png))
            md.write('<img width="49%" src="{}" alt="{}">\n'.format(
                dest_dot_png, dest_dot_png))
            md.write('\n\n')

    print("after copying an initial output to out_ref,")
    print("  you may use: diff -Nsaur dot dot_ref |less")
    print("-------------------------")
    print("how to process and display the output:")
    print("  dot -O -Tpng dot/*.dot")
    print("  plantuml pu/*.pu")
    print("open the generated README.md")


if __name__ == "__main__":
    main()
