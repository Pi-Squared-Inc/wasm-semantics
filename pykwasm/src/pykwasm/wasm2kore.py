import subprocess
import sys
from io import BytesIO
from pathlib import Path

from pyk.kast.inner import KSort
from pyk.ktool.krun import KRun

from .wasm2kast import wasm2kast

def main() -> None:
    # check arg count
    if len(sys.argv) < 3:
        print('usage: wasm2kore <wasm_file> <output_kore_file>')
        sys.exit(1)
    args = sys.argv[1:]

    # parse fixed args
    llvm_dir = Path(args[0])
    wasm_file = Path(args[1])
    kore_file = Path(args[2])
    infile = open(wasm_file, 'rb')

    # parse module as binary (with fallback to textual parser)
    try:
        module = wasm2kast.wasm2kast(infile)
    except Exception:
        proc_res = subprocess.run(['wat2wasm', wasm_file, '--output=/dev/stdout'], check=True, capture_output=True)
        infile.close()
        infile1 = BytesIO(proc_res.stdout)
        module = wasm2kast.wasm2kast(infile1)
        infile1.close()

    # get runner
    runner = KRun(llvm_dir)

    # produce kore
    top_sort = KSort('ModuleDecl')
    module_kore = runner.kast_to_kore(module, top_sort)

    # monkey patch kore writer
    module_kore = PatternWriter(module_kore)

    # write kore to file
    with open(kore_file, 'w') as f:
        module_kore.write(f)


class DepthChange(Enum):
    UP = 1
    DOWN = -1
    PRINT = 0


def pattern_write(pat: Pattern, output: IO[str], pretty=True) -> None:
    """Serialize pattern to kore; used for monkey patch on Pattern object because default write function will blow the stack"""

    if pretty:
        _up, _down, _print = DepthChange.UP, DepthChange.DOWN, DepthChange.PRINT
    else:
        _up, _down, _print = [''] * 3
    not_first_term = False
    print_spacer = False
    depth = 0
    stack = [pat]

    # TODO: fix bug with workitems order

    def push(*items):
        for item in reversed(items):
            if isinstance(item, tuple):
                if len(item) > 1:
                    for subitem in reversed(item[1:]):
                        stack.append(subitem)
                        stack.append(',')
                if len(item) > 0:
                    stack.append(item[0])
            elif isinstance(item, (str, DepthChange)):
                stack.append(item)
            else:
                raise ValueError(f'Unexpected item type: {type(item)}')

    while len(stack) > 0:
        pat = stack.pop()
        if isinstance(pat, str):
            if print_spacer:
                if not_first_term:
                    output.write('\n' + depth * ' ')
                not_first_term = True
                print_spacer = False
            output.write(pat)
        elif isinstance(pat, App):
            push(_print, pat.symbol, '{', pat.sorts, '}(', _up, pat.args, _down, ')')
        elif isinstance(pat, Assoc):
            push(_print, pat.kore_symbol(), '{}(', _up, pat.app, _down, ')')
        elif isinstance(pat, MLPattern):
            push(_print, pat.symbol(), '{', pat.sorts, '}(', pat.ctor_patterns, ')')
        elif isinstance(pat, SortApp):
            push(pat.name, '{', pat.sorts, '}')
        elif isinstance(pat, DepthChange):
            depth += pat.value
            if pat == _print:
                print_spacer = True
        else:
            pat.write(output)


class PatternWriter:
    def __init__(self, pat: Pattern, pretty=False):
        self.pat = pat
        self.pretty = pretty

    def write(self, output: IO[str]):
        if isinstance(self.pat, (App, SortApp, Assoc, MLPattern)):
            pattern_write(self.pat, output, self.pretty)
        else:
            self.pat.write(output)


def debug(pat) -> str:
    if isinstance(pat, str):
        return pat
    elif isinstance(pat, tuple):
        return [debug(item) for item in pat]
    elif isinstance(pat, App):
        return pat.symbol
    elif isinstance(pat, Assoc):
        return pat.kore_symbol()
    elif isinstance(pat, MLPattern):
        return pat.symbol()
    elif isinstance(pat, SortApp):
        return pat.name
    elif isinstance(pat, DepthChange):
        return pat.name
    else:
        return repr(pat)

if __name__ == '__main__':
    main()
