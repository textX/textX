from __future__ import unicode_literals
from textx import metamodel_from_file
from textx.export import metamodel_export, PlantUmlRenderer
import fnmatch
import os
import sys
from os.path import sep, join, dirname, exists


def main(path=None, debug=False, reportfilename=None):
    if path is None:
        path = join(dirname(__file__), "..", "..")
    if reportfilename is None:
        reportfilename = join(dirname(__file__), "REPORT.md")

    print("render_all_grammars.py - example program")
    matches = []
    for root, dirnames, filenames in os.walk(path):
        for filename in fnmatch.filter(filenames, '*.tx'):
            matches.append((root, filename))

    with open(reportfilename, "wt") as md:
        md.write("# All grammars (*.tx)\n")
        for m in matches:
            inname = join(m[0], m[1])
            outfname_base = "{}_{}".format(
                m[0].replace(path, '').lstrip(sep).replace(sep, '_'),
                m[1].rstrip('.tx'))
            destpath = join(dirname(reportfilename), "dot")
            if not exists(destpath):
                os.mkdir(destpath)
            dest_dot = join(destpath, outfname_base + ".dot")
            dest_dot_png = join(destpath, outfname_base + ".dot.png")
            destpath = join(dirname(reportfilename), "pu")
            if not exists(destpath):
                os.mkdir(destpath)
            dest_pu = join(destpath, outfname_base + ".pu")
            dest_pu_png = join(destpath, outfname_base + ".png")

            print(dest_dot)
            mm = metamodel_from_file(inname, debug=debug)
            metamodel_export(mm, dest_dot)
            metamodel_export(mm, dest_pu, renderer=PlantUmlRenderer())

            md.write("## {}\n".format(m[1]))
            md.write(" * source: {}/{}\n".format(m[0], m[1]))
            md.write(" * basename: {}\n".format(outfname_base))
            md.write('\n')
            with open(inname, "rt") as gr:
                for l in gr:
                    md.write("\t\t" + l)
            md.write('\n')
            rel_dest_dot_png = os.path.relpath(
                dest_dot_png, dirname(reportfilename))
            rel_dest_pu_png = os.path.relpath(
                dest_pu_png, dirname(reportfilename))
            md.write('<img width="49%" src="{}" alt="{}">\n'.format(
                rel_dest_pu_png, rel_dest_pu_png))
            md.write('<img width="49%" src="{}" alt="{}">\n'.format(
                rel_dest_dot_png, rel_dest_dot_png))
            md.write('\n\n')

    print("-------------------------")
    print("how to process and display the output:")
    print("  dot -O -Tpng dot/*.dot")
    print("  plantuml pu/*.pu")
    print("open the generated {}".format(reportfilename))


if __name__ == "__main__":
    if len(sys.argv) == 2:
        main(sys.argv[1])
    else:
        main()
