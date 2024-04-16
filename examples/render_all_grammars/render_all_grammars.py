import fnmatch
import os
import sys
from os.path import dirname, exists, join, sep

from textx import metamodel_from_file
from textx.export import PlantUmlRenderer, metamodel_export


def main(path=None, debug=False, reportfilename=None):
    if path is None:
        path = join(dirname(__file__), "..", "..")
    if reportfilename is None:
        reportfilename = join(dirname(__file__), "REPORT.md")

    print("render_all_grammars.py - example program")
    matches = []
    for root, _dirnames, filenames in os.walk(path):
        if 'textx_textx' in root:
            # skip semantically invalid grammars
            continue
        for filename in fnmatch.filter(filenames, '*.tx'):
            matches.append((root, filename))

    with open(reportfilename, "w") as md:
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

            md.write(f"## {m[1]}\n")
            md.write(f" * source: {m[0]}/{m[1]}\n")
            md.write(f" * basename: {outfname_base}\n")
            md.write('\n')
            with open(inname) as gr:
                for i in gr:
                    md.write("\t\t" + i)
            md.write('\n')
            rel_dest_dot_png = os.path.relpath(
                dest_dot_png, dirname(reportfilename))
            rel_dest_pu_png = os.path.relpath(
                dest_pu_png, dirname(reportfilename))
            md.write(f'<img width="49%" src="{rel_dest_pu_png}" '
                     f'alt="{rel_dest_pu_png}">\n')
            md.write(f'<img width="49%" src="{rel_dest_dot_png}" '
                     f'alt="{rel_dest_dot_png}">\n')
            md.write('\n\n')

    print("-------------------------")
    print("how to process and display the output:")
    print("  dot -O -Tpng dot/*.dot")
    print("  plantuml pu/*.pu")
    print(f"open the generated {reportfilename}")


if __name__ == "__main__":
    if len(sys.argv) == 2:
        main(sys.argv[1])
    else:
        main()
