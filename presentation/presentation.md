---
title: 'KWASM: Overview and Path to KeWASM'
author: Everett Hildenbrandt
date: '\today'
theme: metropolis
header-includes:
-   \newcommand{\K}{\ensuremath{\mathbb{K}}}
---

Overview
--------

1.  Introduction to \K{}
2.  KWASM Design
3.  Using KWASM
4.  Future Directions

Introduction to \K{}
====================

The Vision: Language Independence
---------------------------------

Separate development of PL software into two tasks:

. . .

### The Programming Language

PL expert builds rigorous and formal spec of the language in a high-level human-readable semantic framework.

. . .

### The Tooling

Build each tool *once*, and apply it to every language, eg:

-   Parser
-   Interpreter
-   Debugger
-   Compiler
-   Model Checker
-   Program Verifier

The Vision: Language Independence
---------------------------------

![K Tooling Overview](k-overview.png)

Current Semantics
-----------------

Many languages have full or partial \K{} semantics, this lists some notable ones (and their primary usage).

-   [C](https://github.com/kframework/c-semantics): detecting undefined behavior
-   [Java](https://github.com/kframework/java-semantics): detecting racy code
-   [EVM](https://github.com/kframework/evm-semantics): verifying smart contracts
-   [LLVM](https://github.com/kframework/llvm-semantics): compiler validation (to x86)
-   [JavaScript](https://github.com/kframework/javascript-semantics): finding disagreements between JS engines
-   many others ...

\K{} Specifications: Syntax
---------------------------

Concrete syntax built using EBNF style:

```k
    syntax Exp ::= Int | Id | "(" Exp ")" [bracket]
                 | Exp "*" Exp
                 > Exp "+" Exp // looser binding

    syntax Stmt ::= Id ":=" Exp
                  | Stmt ";" Stmt
                  | "return" Exp
```

. . .

This would allow correctly parsing programs like:

```exp
    x := 3 * 2;
    y := 2 * x + 5;
    return y
```

\K{} Specifications: Functional Rules
-------------------------------------

First add the `function` attribute to a given production:

```k
    syntax Int ::= add2 ( Int ) [function]
```

. . .

Then define the function using a `rule`:

```k
    rule add2(I1:Int) => I1 +Int 2
```

\K{} Specifications: Configuration
----------------------------------

Tell \K{} about the structure of your execution state.
For example, a simple imperative language might have:

```k
    configuration <k>     $PGM:Program </k>
                  <env>   .Map         </env>
                  <store> .Map         </store>
```

. . .

> -   `<k>` will contain the initial parsed program
> -   `<env>` contains bindings of variable names to store locations
> -   `<store>` conaints bindings of store locations to integers

\K{} Specifications: Transition Rules
-------------------------------------

Using the above grammar and configuration:

. . .

### Variable lookup

```k
    rule <k> X:Id => V ... </k>
         <env>   ...  X |-> SX ... </env>
         <store> ... SX |-> V  ... </store>
```

. . .

### Variable assignment

```k
    rule <k> X := I:Int => . ... </k>
         <env>   ...  X |-> SX       ... </env>
         <store> ... SX |-> (V => I) ... </store>
```

KWASM Design
============

WASM Specification
------------------

Available at <https://github.com/WebAssembly/spec>.

-   Fairly unambiguous[^betterThanEVM].
-   Well written with procedural description of execution accompanied by small-step semantic rules.

. . .

\newcommand{\instr}{instr}
\newcommand{\LOOP}{\texttt{loop}}
\newcommand{\LABEL}{\texttt{label}}
\newcommand{\END}{\texttt{end}}
\newcommand{\stepto}{\hookrightarrow}

Example rule:

1. Let $L$ be the label whose arity is 0 and whose continuation is the start of the loop.
2. `Enter` the block $\instr^\ast$ with label $L$.

\vspace{-2em}
$$
    \LOOP~[t^?]~\instr^\ast~\END
    \quad \stepto \quad
    \LABEL_0\{\LOOP~[t^?]~\instr^\ast~\END\}~\instr^\ast~\END
$$

[^betterThanEVM]: At least, better than the [YellowPaper](https://github.com/ethereum/yellowpaper).

Translation to \K{}
-------------------

### WASM Spec

\vspace{-1em}
$$
    \LOOP~[t^?]~\instr^\ast~\END
    \quad \stepto \quad
    \LABEL_0\{\LOOP~[t^?]~\instr^\ast~\END\}~\instr^\ast~\END
$$

. . .

### In \K{}

```k
    syntax Instr ::= "loop" Type Instrs "end"
 // -----------------------------------------
    rule <k> loop TYPE IS end
          => IS
          ~> label [ .ValTypes ] {
                loop TYPE IS end
             } STACK
          ...
         </k>
         <stack> STACK </stack>
```

Design Difference: 1 or 2 Stacks?
---------------------------------

. . .

### WASM Specification

Only one stack which mixes values and instructions.
This makes for somewhat confusing semantics for control flow.

For example, when breaking to a label using `br`, the semantics use a meta-level label-context operator.
The correct label must be found in the context (buried in the stack) so we know how many values to take from the top of the stack.
See section 4.4.5 of the WASM spec.

. . .

### KWASM

Uses two stacks, one for values (`<stack>` cell) and one for instructions (`<k>` cell).
Labels are on instruction stack, so no need for context operator as both stacks can be accessed simultaneously.

Design Choice: Incremental Semantics
------------------------------------

KWASM semantics are given incrementally, so that it is possible to execute program fragments.
For example, KWASM will happily execute the following:

```wast
    (i32.const 4)
    (i32.const 5)
    (i32.add)
```

This is despite the fact that no enclosing `module` is present.
This allows users to quickly get to experimenting with WASM using KWASM.