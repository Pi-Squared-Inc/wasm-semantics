

module LIST-REF
  imports WASM-DATA-INTERNAL-SYNTAX
  imports private INT-SYNTAX
  imports private BASIC-K
  imports private MINT-SYNTAX

  syntax Int

  syntax ListRef [hook(LIST.List)]
  syntax ListRef ::= ListRef ListRef
          [ left, function, total, hook(LIST.concat),
            symbol(_ListRef_), smtlib(smt_seq_concat),
            assoc, unit(.ListRef), element(ListRefItem),
            format(%1%n%2)
          ]
  syntax ListRef ::= ".ListRef"
          [ function, total, hook(LIST.unit), symbol(.ListRef),
            smtlib(smt_seq_nil)
          ]
  syntax ListRef ::= ListItem(RefVal)
          [ function, total, hook(LIST.element), symbol(ListRefItem),
            smtlib(smt_seq_elem)
          ]
  syntax RefVal ::= ListRef "[" Int "]"
          [ function, hook(LIST.get), symbol(ListRef:get) ]
  syntax ListRef ::= ListRef "[" index: MInt{64} "<-" value: RefVal "]"
          [function, hook(LIST.update_long), symbol(ListRef:set)]
  syntax ListRef ::= makeListRef(length: Int, value: RefVal)
          [function, hook(LIST.make)]
  syntax ListRef ::= updateList(dest: ListRef, index: Int, src: ListRef)
          [function, hook(LIST.updateAll)]
  syntax ListRef ::= fillList(ListRef, index: Int, length: Int, value: RefVal)
          [function, hook(LIST.fill)]
  syntax ListRef ::= range(ListRef, fromFront: Int, fromBack: Int)
          [function, hook(LIST.range), symbol(ListRef:range)]
  syntax Bool ::= RefVal "in" ListRef
          [function, total, hook(LIST.in), symbol(_inListRef_)]
  syntax MInt{64} ::= size(ListRef)
          [function, total, hook(LIST.size_long), symbol(sizeListRef), smtlib(smt_seq_len)]
endmodule

module LIST-REF-EXTENSIONS
  imports LIST-REF
  imports BOOL
  imports INT
  imports MINT

  syntax RefVal ::= ListRef "[" MInt{64} "]" "orDefault" RefVal
          [ function, total, symbol(ListRef:getOrDefault) ]
// ----------------------------------------------------------------
  rule ListItem(V:RefVal) _:ListRef [N] orDefault _:RefVal
      => V
    requires N ==MInt 0p64
  rule _:ListRef ListItem(V:RefVal) [N] orDefault _:RefVal
      => V
    requires N ==MInt -1p64
  rule .ListRef [_:MInt{64}] orDefault D:RefVal => D

  rule ListItem(_:RefVal) L:ListRef [I:MInt{64}] orDefault D:RefVal
      => L[I -MInt 1p64] orDefault D
    requires 0p64 <sMInt I
  rule L:ListRef ListItem(_:RefVal) [I:MInt{64}] orDefault D:RefVal
      => L[I +MInt 1p64] orDefault D
    requires I <sMInt 0p64

  rule L:ListRef[I:MInt{64}] orDefault D:RefVal => D
    requires notBool (0p64 -MInt size(L)) <=sMInt I andBool I <sMInt size(L)
    [simplification]

  syntax RefVal ::= getRefOrNull(ListRef, MInt{64})
          [ function, total, symbol(ListRef:getOrNull) ]
// -------------------------------------------------------------
  rule getRefOrNull(L, N) => L [N] orDefault (<funcref> null)

  syntax ListRef ::= makeListRefTotal(MInt{32}, RefVal)
      [function, total, symbol(ListRef:makeTotal)]
// ----------------------------------------------------
  rule makeListRefTotal(N, V) => makeListRef(MInt2Unsigned(N), V)
  
  syntax ListRef ::= dropListRef(MInt{32}, ListRef)
      [function, total, symbol(ListRef:drop)]
// --------------------------------------------------------------
  rule dropListRef(N, ListItem(_) L) => dropListRef(N -MInt 1p32, L)
    requires N =/=MInt 0p32
  rule dropListRef(_, L)             => L
    [owise]
  
endmodule
