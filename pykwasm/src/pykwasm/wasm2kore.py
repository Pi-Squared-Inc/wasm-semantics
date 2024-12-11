import subprocess
import sys
from io import BytesIO
from pathlib import Path

from pyk.kast.inner import KSort
from pyk.ktool.krun import KRun

from . import wasm2kast

sys.setrecursionlimit(10**6)

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

    top_sort = KSort('ModuleDecl')
    config_kore = runner.kast_to_kore(module, top_sort)

    print(f"Writing to {kore_file}")
    kore_file.write_text(config_kore.text)
    # # monkey patch kore
    # patched_config_kore = PatternWriter(config_kore)
    # with open(wasm_file.name + '.input.kore', e'w') as f:
    #     patched_config_kore.write(f)

if __name__ == '__main__':
    main()
