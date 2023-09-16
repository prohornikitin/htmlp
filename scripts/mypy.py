#!/usr/bin/env python
from pathlib import Path
import subprocess
import os


SCRIPTS_DIR = Path(__file__).parent.absolute()
ROOT_DIR = SCRIPTS_DIR.parent
SRC_DIR = (ROOT_DIR / 'src')


if __name__ == '__main__':
    env = os.environ.copy()
    env['MYPYPATH'] = str(SRC_DIR.absolute())
    process = subprocess.Popen(
        [
            'mypy', '--explicit-package-bases', str(SRC_DIR), str(SCRIPTS_DIR)
        ],
        env=env,
    )
    process.communicate()
    exit(process.returncode)
