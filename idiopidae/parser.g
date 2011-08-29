### @export starter

# Copyright (C) Zed A. Shaw, licensed under the GPLv3

import idiopidae.runtime

%%

### @export grammar
parser IdiopidaeParser:

    ### @export tokens
    token WS: "[ \t]+"
    token NUMBER: "[0-9]+[0-9\.]*"
    token STRING: '\'([^\\n\'\\\\]|\\\\.)*\'|"([^\\n"\\\\]|\\\\.)*"'
    token EOD: "\\0"
    token EOL: "(\\n|\\r\\n)"
    token END: "end"
    token ID: "[a-zA-Z][a-zA-Z\-_0-9]+"
    token INCLUDE: "include"
    token EXPORT: "export"
    token STARTER: "[ \t]*(###|//|\\*)+ @"
    token NOT_STARTER: "([^#]|[^//]|[^\\*])"
    token JUNK: "[^\\n]*" 

    ### @export rules
    rule Section:  
            ID {{ return ID }} 
            | NUMBER {{ return NUMBER }} 
            | STRING {{ return STRING[1:-1] }}
    rule Language: WS ID {{ return ID }} 
    rule Format:   WS ID {{ return ID }}
    rule File: STRING {{ return STRING[1:-1] }}
    rule Include: 
        INCLUDE WS File WS Section Format? {{ self.doc.include(File, Section, Format) }}
    rule Export: EXPORT WS Section Language?  {{ self.doc.export(Section, Language) }}
    rule Command: Include 
        | Export 
        | END {{ self.doc.end() }}
    rule Statement: STARTER Command (WS)* EOL
    rule Junk: (
            NOT_STARTER JUNK EOL {{ self.doc.append(NOT_STARTER + JUNK) }}
            | EOL {{ self.doc.append('') }}
            )
    rule Line: Statement | Junk 
    rule Document: 
        {{ self.doc = idiopidae.runtime.Builder() }} 
        (Line)* 
        EOD {{ self.doc.append_current_export();  return self.doc }}

