from idiopidae import parser
from nose.tools import *

def test_scanning():
    scanner = parser.IdiopidaeParserScanner(
        """12.3 "12" \0 \n end an_id include export ### @ """)

    patterns = [
        'NUMBER', 'WS', 'STRING', 'WS',
        'EOD', 'WS', 'EOL', 'WS', 'END', 'WS',
        'ID', 'WS', 'INCLUDE', 'WS', 'EXPORT', 'WS',
        'STARTER', 'WS',]

    for pattern in patterns: scanner.scan(pattern)

    for token,pattern in zip(scanner.tokens, patterns):
        assert_equal(token[2],pattern,"Token %s didn't match pattern %s" % (repr(token), repr(pattern)))


def test_eat():
    scanner = parser.IdiopidaeParserScanner("12345678901234567890")
    assert_equal("1234567890", scanner.eat(10))
    assert_equal("12345", scanner.eat(5))
    assert_equal("67890", scanner.eat(5))


def test_skip():
    scanner = parser.IdiopidaeParserScanner("12345678901234567890")
    scanner.skip(10)
    assert_equal("12345", scanner.eat(5))
    assert_equal("67890", scanner.eat(5))


def test_junk():
    scanner = parser.IdiopidaeParserScanner("not starter and some junk")
    scanner.scan('NOT_STARTER')
    scanner.scan('JUNK')

