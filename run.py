#!/usr/bin/env python3
"""Launcher for Segfault.

Auto-bootstraps into the project's .venv (which has a working pygame-ce) so you
can just run `python3 run.py` with any interpreter and it does the right thing.
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


VENV_DIR = os.path.join(HERE, ".venv")


def _venv_python():
    for sub in ("bin/python", "bin/python3", "Scripts/python.exe"):
        p = os.path.join(VENV_DIR, sub)
        if os.path.exists(p):
            return p
    return None


def _in_venv():
    # venv's bin/python is a symlink to the base interpreter, so we can't
    # compare executables; compare prefixes instead.
    return os.path.realpath(sys.prefix) == os.path.realpath(VENV_DIR)


def main():
    vp = _venv_python()
    if vp and not _in_venv():
        # re-exec inside the venv so pygame-ce (with font + mixer) is used
        os.execv(vp, [vp, os.path.abspath(__file__), *sys.argv[1:]])

    sys.path.insert(0, HERE)
    from segfault.main import main as game_main
    game_main()


if __name__ == "__main__":
    main()
