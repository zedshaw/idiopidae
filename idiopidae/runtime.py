from __future__ import with_statement

# Copyright (C) Zed A. Shaw, licensed under the GPLv3

import idiopidae.parser
from pygments import highlight
from pygments.formatters import get_formatter_for_filename, get_formatter_by_name
from pygments.lexers import guess_lexer_for_filename, get_lexer_by_name


### @export "Builder Class"
class Builder(object):
    """Used by IdiopidaeParser to construct the data structure of
        a parsed document.  Composer then uses this to unify a file
        against a directory of other files to produce an output."""


    def __init__(self):
        self.index = 0
        self.line = 1
        self.current = {
                "command": "export", "section": self.next_anonymous(), 
                "language": None, 
                "lines": []}
        self.statements = [self.current]
        self.exports = {}
        self.sections = []


    ### @export "Main Methods: include, export, append"
    def include(self, file, section, format):
        """ Creates a new include statement which lines are next appended to."""
        self.next_statement({
            "command": "include", 
            "file": file, 
            "section": section, 
            "format": format,
            "language": None,
            "lines": []
            })


    def export(self, section, language):
        """ Creates a new export statement which lines are next appended to."""
        if not section: section = self.next_anonymous()

        self.next_statement({
            "command": "export", 
            "section": section, 
            "language": language,
            "lines": []})


    def end(self):
        """Just a method that ends a section to start the
        next anonymous one."""
        self.export(None, None)


    def append(self, text):
        """ Appends a line to the current statement with line numbers."""
        self.current["lines"].append((self.line, text))
        self.line += 1


    ### @export "Things You Call"
    def lines_for(self, section):
        """Returns the lines for a given section, as tuple pairs
            of (line number, text)."""
        return self.exports[section]["lines"]


    def dump(self):
        gutter = len("%d" % self.line)
        format = "".join(["%",str(gutter),"d: %s"])
        for section in self.sections:
            print "--- %s" % section
            for line in self.lines_for(section):
                print format % (line[0], repr(line[1]))


    ### @export next_statement
    def next_statement(self, statement):
        """Just slaps this new statement onto the list of existing
           statements and then sets the current one for appending
           the lines."""
        self.append_current_export()
        self.current = statement
        self.statements.append(self.current)

    def next_anonymous(self):
        """Increments the anonymous section counter for tracking
        sections without names."""
        self.index += 1
        return str(self.index)

    ### @export append_current_export
    def append_current_export(self):
        """When a new export statement is hit, this updates the 
           internals that track sequential export statements 
           for later analysis."""
        if self.current["command"] == "export":
            section = self.current["section"]
            self.exports[section] = self.current
            self.sections.append(section)
### @end


### @export "Composer Class"
class Composer(object):
    """Uses idiopidae.parser.parse to parse the given file into a 
    builder, and then spits out the results using the self.process()
    method."""

    def __init__(self):
        self.includes = {}
        self.loads = {}


    ### @export "How Files Are Loaded"
    def load(self, name):
        """Does the actual parsing of a file into a Builder and caches the results
        into self.loads for faster calls later."""
        if not self.loads.has_key(name):
            with open(name) as file:
                text = file.read() + "\n\0"
                self.loads[name] = idiopidae.parser.parse('Document', text)
        return self.loads[name]
    ### @end


    ### @export "How Files Are Processed"
    def process(self, name):
        """Performs a full processing of the file returning a string
        with all the @include sections replaced."""
        self.builder = self.load(name)
        results = []
        for st in self.builder.statements:
            if st["command"] == "export":
                self.append_export(results, st)
            elif st["command"] == "include":
                self.append_include(results, name, st)
        return "\n".join(results)

    def append_include(self, results, name, st):
        key = "%s/%s/%s" % (name, st["file"], st["section"])

        if self.includes.has_key(key):
            # look it up in the cache instead of processing it again
            text = self.includes[key]
        else:
            lines, firsts = self.include(st["file"], st["section"])
            lexer = self.resolve_lexer(st, firsts)
            format = self.resolve_format(name, st, lines[0][0])
            text = self.format(lines, lexer, format)
            self.includes[key] = text

        results.append(text)

    def append_export(self, results, st):
        results.append(self.format(st["lines"]))


    def resolve_lexer(self, st, firsts):
        """Responsible for resolving the lexer that should be used on the
        section of code.  It will use the one specified in the export, and
        then try to guess based on the file name/extension and the first line
        of the text file."""
        file, lang = st["file"], st["language"]

        if lang:
            return get_lexer_by_name(lang)
        try:
            return guess_lexer_for_filename(file, firsts)
        except:
            return get_lexer_by_name("text")
        

    def resolve_format(self, file, st, first_line=0, linenos=False):
        """Resolves formats that are specified based on either the
        file name/extension or an explicitly given format."""
        # TODO: let them specify options too, probably from some yaml
        if st["format"]:
            return get_formatter_by_name(st["format"], linenos=linenos,
                                         linenostart=first_line)
        else:
            try:
                return get_formatter_for_filename(file, linenos=linenos,
                                         linenostart=first_line)
            except:
                return get_formatter_by_name("text", linenos=linenos,
                                         linenostart=first_line)

    ### @export "Formatting Lines With or Without Numbers"
    def format(self, lines, lexer = None, format = None):
        """Given a set of (#,"") line tuples it will return a 
        string with line numbers or not."""
        text = "\n".join([l[1] for l in lines])

        if format and lexer:
            return highlight(text.rstrip(), lexer, format)
        else:
            return text


    ### @export "How Other Sections Are Included"
    def include(self, file, section):
        """Loads the requested section and returns those lines and the first
        few lines of the whole file for guessing the format.  Also does some 
        caching of the requested sections, firsts, and loaded files."""

        try:
            target = self.load(file)
            if not target: 
                print "!!!! ERROR: Failed to parse file %s (see above for error)" % file
                raise RuntimeError("ERROR: Failed to parse %s (see output)" % file)
            else:
                lines = target.lines_for(section)
                firsts = self.format(target.lines_for(target.sections[0]))

            return lines, firsts
        except KeyError:
            raise KeyError("ERROR: Key '%s' not exported or included in file '%s'" % (section, file))

