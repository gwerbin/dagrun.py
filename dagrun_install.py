r"""Installer for dagrun.py"""

import os
import platform
import stat
import sys
from argparse import ArgumentParser
from pathlib import Path

def main() -> int | None:
    arg_parser = ArgumentParser()
    arg_parser.add_argument("-p", "--python", default=sys.executable, help=f"The Python executable to use for the dagrun script. Default: the current executable ({sys.executable}).")
    arg_parser.add_argument("-o", "--output", default="./dagrun.py", help="The filename to use for the dagrun script. Default: `./dagrun.py`. If `-`, send to stdout.")
    arg_parser.add_argument("-f", "--force", action="store_true", default=False, help="Force overwriting existing output file.")
    cli_args = arg_parser.parse_args()

    import dagrun

    source = Path(dagrun.__file__)
    if cli_args.output.strip() == "-":
        dest = sys.stdout
    else:
        dest = Path(cli_args.output)

    with source.open() as fp:
        code = fp.read()

    code = f"#!{sys.executable}\n\n" + code
    if dest is sys.stdout:
        print(code)
    else:
        if dest.exists() and not cli_args.force:
            print(f"Refusing to overwrite existing output file: {dest}", file=sys.stderr)
            return 1
        with dest.open("w") as fp:
            fp.write(code)
        # os.chmod(dest, 0o755)
        if platform.system() != "Windows":
            perm = (
                stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR |
                stat.S_IRGRP | stat.S_IXGRP |
                stat.S_IROTH | stat.S_IXOTH
            )
            print(perm)
            os.chmod(dest, perm)

    return None


if __name__ == "__main__":
    sys.exit(main())
