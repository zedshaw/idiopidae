# Copyright (C) Zed A. Shaw, licensed under the GPLv3

from idiopidae.runtime import *
from nose.tools import *

def test_load():
    comp = Composer()
    doc = comp.load("tests/data/test.py")
    assert doc
    assert_equal(len(doc.sections), 5, "wrong number of sections")

def test_process():
    comp = Composer()
    assert len(comp.process("tests/data/test.py")) > 0
    assert len(comp.process("tests/data/output.html")) > 0
    assert len(comp.process("doc/src/index.page")) > 0

def test_resolve_lexer():
    comp = Composer()
    combos = [
    ({ "file": "test.py", "firsts": "#!/usr/bin/env python", "language": None }, "Python"),
    ({ "file": "test.py", "firsts": "#!/usr/bin/env python", "language": "python" }, "Python"),
    ({ "file": "test", "firsts": "#!/usr/bin/env python", "language": "python" }, "Python"),
    ({ "file": "test.blah", "firsts": "", "language": None }, "Text only"),
    ]

    for data, expected_name in combos:
        lex = comp.resolve_lexer(data, data["firsts"])
        assert lex
        assert lex.name == expected_name, "expected lexer: %s but got %s" % (expected_name, lex.name)

def test_resolve_format():
    comp = Composer()
    combos = [
    ("output.html", {"format": "html"}, "HTML"),
    ("output.html", {"format": None}, "HTML"),
    ("output.txt", {"format": None}, "Text only"),
    ("output.blah", {"format": None}, "Text only"),
    ("output.blah", {"format": "latex"}, "LaTeX"),
    ]

    for file, format, expected_name in combos:
        format = comp.resolve_format(file, format)
        assert format
        assert_equal(format.name, expected_name, "didn't get format we wanted: %s != %s" % (format.name, expected_name))

def test_format():
    comp = Composer()
    lines = [(1, "line 1"), (2, "line 2")]
    assert comp.format(lines) == "line 1\nline 2"

    # now with a lexer and formatter
    lexer = comp.resolve_lexer({"file": "test.py", "language": "python"}, "#!/usr/bin/env python")
    assert lexer
    format = comp.resolve_format("output.html", {"format": "html"})
    assert format

    assert comp.format(lines, lexer, format)

def test_include():
    comp = Composer()
    lines, firsts = comp.include("tests/data/test.py", "1")
    assert comp.format(lines) == firsts, "firsts and the first lines of the first section should be the same"
    
    # try to make it blow up with an illegal section
    assert_raises(KeyError, comp.include, "tests/data/test.py", "not a legal section")

