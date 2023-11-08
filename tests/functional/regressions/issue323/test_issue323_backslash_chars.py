from os.path import abspath, dirname, join

from textx import metamodel_from_file, metamodel_from_str

grammars = [
    # String match with backslash chars
    r"""
    Rule1[noskipws]: 'First' '\n' Rule2;
    Rule2: / */- 'Second' '\t' 'Third';
    """,
    # Regex match with backslash chars
    r"""
    Rule1[noskipws]: 'First' /\n/ Rule2;
    Rule2: / */- 'Second' /\t/ 'Third';
    """,
]


def test_newline_str_match_in_raw_str():
    for grammar in grammars:
        mm = metamodel_from_str(grammar)
        model = mm.model_from_str(
            """First
            Second\tThird"""
        )

        assert model == "First\nSecond\tThird"


def test_newline_str_match_in_files():
    this_folder = dirname(abspath(__file__))
    for grammar in range(1, 3):
        mm = metamodel_from_file(join(this_folder, f"grammar{grammar}.tx"))
        model = mm.model_from_str(
            """First
            Second\tThird"""
        )

        assert model == "First\nSecond\tThird"
