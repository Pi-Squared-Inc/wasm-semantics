```k
requires "wasm-text.md"
requires "ulm.k"
```

```k
module ULM-WASM-SYNTAX
  imports WASM-TEXT-SYNTAX
endmodule
```

```k
module ULM-WASM
  imports WASM-TEXT
  imports ULM
```

Configuration
-------------

```k
    configuration
      <ulm-wasm>
        <k> $PGM:Stmts </k>
        <wasm/>
      </ulm-wasm>
```

Passing Control
---------------

The test embedder sets up the built-in module and passes control to the execution cell in Wasm.

```k
    rule <k> PGM => .K </k>
         <instrs> .K
               => #emptyModule()
               ~> sequenceStmts(text2abstract(PGM))
         </instrs>
```

Instruction sugar
-----------------

We allow writing instructions at the top level in the test embedder.

```k
    rule <instrs> FI:FoldedInstr => sequenceInstrs(unfoldInstrs(FI .Instrs)) ... </instrs>
```

```k
endmodule
```
