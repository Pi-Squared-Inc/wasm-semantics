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
    syntax OutputData ::= "NO_OUTPUT"
                        | Bytes

    configuration
      <ulmWasm>
        <k> $PGM:Bytes </k>
        <wasm/>
        <createMode> $CREATE:Bool </createMode>
        <wasmGas> $GAS:Int </wasmGas>
        <wasmStatus> EVMC_INTERNAL_ERROR </wasmStatus>
        <wasmOutput> NO_OUTPUT </wasmOutput>
      </ulmWasm>
```

Passing Control
---------------

The test embedder sets up the built-in module and passes control to the execution cell in Wasm.

```k
    syntax ModuleDecl ::= decodeModule(Bytes) [function, hook(ULM.decode)]

    rule <k> PGM:Bytes => .K </k>
         <instrs> .K
               => #emptyModule()
               ~> sequenceStmts(text2abstract(decodeModule(PGM)))
         </instrs>
```

Instruction sugar
-----------------

We allow writing instructions at the top level in the test embedder.

```k
    rule <instrs> FI:FoldedInstr => sequenceInstrs(unfoldInstrs(FI .Instrs)) ... </instrs>
```

ULM Hook Behavior
-----------------

These rules define various integration points between the ULM and our Wasm interpreter.

**Note**: the first three rules hooks below are written with helper functions
          because parse errors were encountered when writing `<generatedTopCell>` literals.

```k
    syntax Int ::= #getGasLeft() [function, total]
    rule [[ #getGasLeft() => Gas ]]
         <wasmGas> Gas:Int </wasmGas>

    syntax Bytes ::= #getOutput() [function, total]
    rule [[ #getOutput() => #if OutVal ==K NO_OUTPUT #then .Bytes #else {OutVal}:>Bytes #fi ]]
         <wasmOutput> OutVal:OutputData </wasmOutput>

    syntax Int ::= #getStatus() [function, total]
    rule [[ #getStatus() => #if OutVal ==K NO_OUTPUT #then EVMC_INTERNAL_ERROR #else Status #fi ]]
         <wasmOutput> OutVal:OutputData </wasmOutput>
         <wasmStatus> Status:Int </wasmStatus>

    rule getGasLeft(_) => #getGasLeft()
    rule getOutput(_)  => #getOutput()
    rule getStatus(_)  => #getStatus()
```

```k
endmodule
```
