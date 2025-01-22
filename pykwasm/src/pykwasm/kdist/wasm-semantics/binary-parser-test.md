```k
requires "binary-parser.md"
requires "wasm.md"

module BINARY-PARSER-TEST-SYNTAX
endmodule

module BINARY-PARSER-TEST
    imports BINARY-PARSER-TEST-SYNTAX

    imports BINARY-PARSER
    imports BINARY-PARSER-SYNTAX
    imports BINARY-PARSER-MODULE-TEST-SYNTAX
    imports BINARY-PARSER-SECTION-SYNTAX

    syntax KItem ::= parseBinary(Bytes)

    configuration
        <k> parseBinary($PGM) </k>
        <wasm/>


    rule parseBinary(B:Bytes) => parseModule(B)

    rule addDefnToModule
            ( false => true
            , _D:GlobalDefn
            , #module(... metadata: _ => #meta (... id:  , funcIds: .Map , filename: "error: test addDefnToModule(GlobalDefn) branch called." )))
        [owise]
    rule addDefnToModule
            ( false => true
            , _D:MemoryDefn
            , #module(... metadata: _ => #meta (... id:  , funcIds: .Map , filename: "error: test addDefnToModule(MemoryDefn) branch called." )))
        [owise]
    rule addDefnToModule
            ( false => true
            , _D:ElemDefn
            , #module(... metadata: _ => #meta (... id:  , funcIds: .Map , filename: "error: test addDefnToModule(ElemDefn) branch called." )))
        [owise]
    rule addDefnToModule
            ( false => true
            , _D:DataDefn
            , #module(... metadata: _ => #meta (... id:  , funcIds: .Map , filename: "error: test addDefnToModule(DataDefn) branch called." )))
        [owise]
    rule addDefnToModule
            ( false => true
            , _D:StartDefn
            , #module(... metadata: _ => #meta (... id:  , funcIds: .Map , filename: "error: test addDefnToModule(StartDefn) branch called." )))
        [owise]
    rule addDefnToModule
            ( false => true
            , _D:ExportDefn
            , #module(... metadata: _ => #meta (... id:  , funcIds: .Map , filename: "error: test addDefnToModule(ExportDefn) branch called." )))
        [owise]
    rule addDefnToModule
            ( false => true
            , _D:Defn
            , #module(... metadata: _ => #meta (... id:  , funcIds: .Map , filename: "error: test addDefnToModule branch called." )))
        [priority(250)]

endmodule
```
