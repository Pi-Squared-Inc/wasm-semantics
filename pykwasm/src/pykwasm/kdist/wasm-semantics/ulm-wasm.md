```k
requires "wasm-text.md"
requires "ulm.k"
```

```k
module ULM-WASM-COMMON-SYNTAX
   imports WASM-TEXT-COMMON-SYNTAX
   imports BOOL-SYNTAX
   imports INT-SYNTAX
```

Program Encoding
----------------

The ULM-integrated WASM VM has two possible program encodings:

1.  In the local test VM case, a direct encoding is used.

    ```local
    syntax PgmEncoding ::= Stmts
    ```

2.  In the remote ULM-integrated VM case, a byte encoding is used.

    ```remote
    imports BYTES-SYNTAX
    syntax PgmEncoding ::= Bytes
    ```

```k
endmodule
```

```k
module ULM-WASM-SYNTAX
    imports ULM-WASM-COMMON-SYNTAX
    imports WASM-TEXT-SYNTAX
endmodule
```

```k
module ULM-WASM
    imports ULM-WASM-COMMON-SYNTAX
    imports WASM-TEXT
    imports ULM
```

Program Decoding
----------------

The WASM VM must decode the input program:

1.  In local test VM case, the decoding function is just identity.

    ```local
    syntax Stmts ::= decodePgm(Stmts) [function, total]
    // ------------------------------------------------
    rule decodePgm(Stmts) => Stmts
    ```

2.  In the remote ULM-integrated VM case, a specialized, hooked byte decoder is used.

    ```remote
    syntax ModuleDecl ::= decodePgm(Bytes) [function, hook(ULM.decode)]
    ```

Configuration
-------------

Here we define the initial configuration.
Note that the default status code indicates an internal error; this is used defensively, since if we ever get stuck, an error will always be indicated.
Similarly, we define a default null output which may indicate internal errors.

```k
    syntax OutputData ::= "NO_OUTPUT"
                        | Bytes

    configuration
      <ulmWasm>
        <k> $PGM:PgmEncoding </k>
        <wasm/>
        <createMode> $CREATE:Bool </createMode>
        <wasmEntrypoint> $WASM:String </wasmEntrypoint>
        <wasmGas> $GAS:Int </wasmGas>
        <wasmStatus> EVMC_INTERNAL_ERROR </wasmStatus>
        <wasmOutput> NO_OUTPUT </wasmOutput>
      </ulmWasm>
```

Passing Control
---------------

The embedder loads the module to be executed and then resolves the entrypoint function.

```k
    rule <k> PGM:PgmEncoding => #resolveCurModuleFuncExport(FUNCNAME) </k>
         <wasmEntrypoint> FUNCNAME </wasmEntrypoint>
         <instrs> .K
               => sequenceStmts(text2abstract(decodePgm(PGM)))
         </instrs>
```

Note that entrypoint resolution must occur _after_ the Wasm module has been loaded.
This is ensured by requiring that the `<instrs>` cell is empty during resolution.

```k
    syntax Initializer ::= #resolveCurModuleFuncExport(String)
                         | #resolveModuleFuncExport(Int, String)
                         | #resolveFunc(Int, List)
    // -------------------------------------------
    rule <k> #resolveCurModuleFuncExport(FUNCNAME) => #resolveModuleFuncExport(MODIDX, FUNCNAME) </k>
         <instrs> .K </instrs>
         <curModIdx> MODIDX:Int </curModIdx>

    rule <k> #resolveModuleFuncExport(MODIDX, FUNCNAME) => #resolveFunc(FUNCIDX, FUNCADDRS) </k>
         <instrs> .K </instrs>
         <moduleInst>
           <modIdx> MODIDX </modIdx>
           <exports> ... FUNCNAME |-> FUNCIDX ... </exports>
           <funcAddrs> FUNCADDRS </funcAddrs>
           ...
         </moduleInst>

    rule <k> #resolveFunc(FUNCIDX, FUNCADDRS) => .K </k>
         <instrs> .K => (invoke FUNCADDRS {{ FUNCIDX }} orDefault -1 ):Instr </instr>
         requires isListIndex(FUNCIDX, FUNCADDRS)
```

Here we handle the case when entrypoint resolution fails.

**TODO:** Decide how to handle failure case.

```k
    // rule <k> Init:Initializer => . </k> [owise]
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
