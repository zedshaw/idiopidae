from __future__ import with_statement
from idiopidae import parser
from nose.tools import *


def parse_file(name, what="Document"):
    with open(name) as file:
        text = file.read() + "\n\0"
        doc = parser.parse(what, text)
        assert doc, "Failed to parse %s from file %s" % (what, name)
        return doc

def parse_lines(lines, what='Document'):
    results = [parser.parse(what, l+'\n\0') for l in lines]
    for result in results:
        assert result
    return results

def test_document():
    doc = parse_file("tests/data/test.py")
    assert_equal(len(doc.exports), 5, "Wrong number of exported sections")


    doc = parse_file("doc/src/index.page")
    assert len(doc.exports) > 0, "Expected some form of exports or includes"


def test_line():
    lines = ['### @export "test section"', 
            '### @export "test section" python', 
            '### @include "test.py" 1', 
            '### @include "test.py" 1 python', 
            '### @end', 
            'this is junk',
            '### this is junk'
            ]
    results = parse_lines(lines)
    for result in results:
        assert len(result.exports) > 0


def test_junk():
    lines = ['junk of stuff that should be',
            '#@ this should not match either',
            '###@ this should not match',
            '\n',
            'totally screwy\n']
    results = parse_lines(lines)
    for result in results:
        assert len(result.exports) > 0

def test_statement():
    lines = ['### @export 3', 
            '### @export 3 python', 
            '### @include "test.py" 1', 
            '### @include "test.py" 1 python', 
            '### @end',
            ]
    results = parse_lines(lines)
    for result in results:
        assert len(result.exports) > 0

def test_file():
    lines = ['"afile.py"', "'afile.py'"]
    results = parse_lines(lines, 'File')

def test_format():
    lines = [' html', ' latex']
    results = parse_lines(lines, 'Format')
    for r,l in zip(results, lines):
        assert_equal(r, l.strip(), "result %s didn't match line %s" % (repr(r),repr(l)))

def test_language():
    lines = [' python', ' ruby']
    results = parse_lines(lines, 'Language')
    for r,l in zip(results, lines):
        assert_equal(r, l.strip(), "result %s didn't match line %s" % (repr(r),repr(l)))

def test_section():
    lines = ['an_id', 'another_id', 'id234',
            '13454','12.4']
    results = parse_lines(lines, 'Section')
    for r,l in zip(results, lines):
        assert_equal(r, l, "result %s didn't match line %s" % (repr(r),repr(l)))

def test_quoted_section():
    result = parse_lines(['"Section 2.4"'], 'Section')
    assert_equal(result[0], "Section 2.4")


