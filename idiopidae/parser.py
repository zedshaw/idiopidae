### @export starter

# Copyright (C) Zed A. Shaw, licensed under the GPLv3

import idiopidae.runtime


from string import *
import re
from zapps.rt import *

class IdiopidaeParserScanner(Scanner):
    patterns = [
        ('WS', re.compile('[ \t]+')),
        ('NUMBER', re.compile('[0-9]+[0-9\\.]*')),
        ('STRING', re.compile('\'([^\\n\'\\\\]|\\\\.)*\'|"([^\\n"\\\\]|\\\\.)*"')),
        ('EOD', re.compile('\\0')),
        ('EOL', re.compile('(\\n|\\r\\n)')),
        ('END', re.compile('end')),
        ('ID', re.compile('[a-zA-Z][a-zA-Z\\-_0-9]+')),
        ('INCLUDE', re.compile('include')),
        ('EXPORT', re.compile('export')),
        ('STARTER', re.compile('[ \t]*(###|//|\\*)+ @')),
        ('NOT_STARTER', re.compile('([^#]|[^//]|[^\\*])')),
        ('JUNK', re.compile('[^\\n]*')),
    ]
    def __init__(self, str):
        Scanner.__init__(self,None,[],str)

class IdiopidaeParser(Parser):
    def Section(self):
        _token_ = self._peek('ID', 'NUMBER', 'STRING')
        if _token_ == 'ID':
            ID = self._scan('ID')
            return ID
        elif _token_ == 'NUMBER':
            NUMBER = self._scan('NUMBER')
            return NUMBER
        else:# == 'STRING'
            STRING = self._scan('STRING')
            return STRING[1:-1]

    def Language(self):
        WS = self._scan('WS')
        ID = self._scan('ID')
        return ID

    def Format(self):
        WS = self._scan('WS')
        ID = self._scan('ID')
        return ID

    def File(self):
        STRING = self._scan('STRING')
        return STRING[1:-1]

    def Include(self):
        INCLUDE = self._scan('INCLUDE')
        WS = self._scan('WS')
        File = self.File()
        WS = self._scan('WS')
        Section = self.Section()
        if self._peek('WS', 'EOL') == 'WS':
            Format = self.Format()
        else:
            Format = None

        self.doc.include(File, Section, Format)

    def Export(self):
        EXPORT = self._scan('EXPORT')
        WS = self._scan('WS')
        Section = self.Section()
        if self._peek('WS', 'EOL') == 'WS':
            Language = self.Language()
        else:
            Language = None

        self.doc.export(Section, Language)

    def Command(self):
        _token_ = self._peek('INCLUDE', 'EXPORT', 'END')
        if _token_ == 'INCLUDE':
            Include = self.Include()
        elif _token_ == 'EXPORT':
            Export = self.Export()
        else:# == 'END'
            END = self._scan('END')
            self.doc.end()

    def Statement(self):
        STARTER = self._scan('STARTER')
        Command = self.Command()
        while self._peek('WS', 'EOL') == 'WS':
            WS = self._scan('WS')
        EOL = self._scan('EOL')

    def Junk(self):
        _token_ = self._peek('NOT_STARTER', 'EOL')
        if _token_ == 'NOT_STARTER':
            NOT_STARTER = self._scan('NOT_STARTER')
            JUNK = self._scan('JUNK')
            EOL = self._scan('EOL')
            self.doc.append(NOT_STARTER + JUNK)
        else:# == 'EOL'
            EOL = self._scan('EOL')
            self.doc.append('')

    def Line(self):
        _token_ = self._peek('STARTER', 'NOT_STARTER', 'EOL')
        if _token_ == 'STARTER':
            Statement = self.Statement()
        else:# in ['NOT_STARTER', 'EOL']
            Junk = self.Junk()

    def Document(self):
        self.doc = idiopidae.runtime.Builder()
        while self._peek('STARTER', 'NOT_STARTER', 'EOL', 'EOD') != 'EOD':
            Line = self.Line()
        EOD = self._scan('EOD')
        self.doc.append_current_export();  return self.doc


def parse(rule, text):
    P = IdiopidaeParser(IdiopidaeParserScanner(text))
    return wrap_error_reporter(P, rule)

if __name__ == '__main__':
    from sys import argv, stdin
    if len(argv) >= 2:
        if len(argv) >= 3:
            f = open(argv[2],'r')
        else:
            f = stdin
        print parse(argv[1], f.read())
    else: print 'Args:  <rule> [<filename>]'
