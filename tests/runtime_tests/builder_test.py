from idiopidae.runtime import Builder
from nose.tools import *


def extend_builder(b):
    b.append("line -1")
    b.append("line 0")
    b.include("test.py", "Sample Import", "html")
    b.append("line 1")
    b.append("line 2")
    b.export("Sample Export", "python")
    b.append("line 3")
    b.append("line 4")
    b.end()
    b.append("line 5")
    b.append("line 6")


def test_include():
    build = Builder()
    build.include("test.py", "1.0", "html")
    assert_equal( len(build.exports), 1, "include didn't create a new section")


def test_export():
    build = Builder()
    build.export("1.0", "python")
    assert_equal( len(build.exports), 1, "export didn't create new section")


def test_end():
    build = Builder()
    build.export("Test","python")
    build.end()
    assert_equal( len(build.exports), 2, "end didn't start a new anonymous section")


def test_append():
    build = Builder()
    extend_builder(build)
    for section in build.sections:
        # the first section is a dud, so just skip it
        if section != "1":
            build.exports[section]
            line_count = len(build.exports[section]["lines"])
            assert_equal( line_count, 2, "section %s count: %d != 2" % (section, line_count ))


def test_lines_for():
    build = Builder()
    extend_builder(build)
    for section in build.sections:
        if section != "1":
            assert build.lines_for(section)
            print section, build.lines_for(section)
            assert_equal( len(build.lines_for(section)), 2, "lines for section %s != 2" % (section))


def test_next_statement():
    build = Builder()
    build.next_statement({
            "command": "include", 
            "file": "test.py", 
            "section": "test section", 
            "format": "html",
            "lines": []
            })
    assert_equal(len(build.exports), 1)
    assert_equal(len(build.sections), 1)

    build.next_statement({
            "command": "export", 
            "section": "test other section", 
            "language": "python",
            "lines": []})
    build.end()
    assert_equal(len(build.exports), 2)


def test_next_anonymous():
    build = Builder()
    assert_equal(build.index, 1)
    assert_equal(build.next_anonymous(), "2")


def test_append_current_export():
    test_next_statement()  # this tests that


def test_dump():
    Builder().dump()

