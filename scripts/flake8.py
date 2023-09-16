#!/usr/bin/env python
from pathlib import Path
import subprocess


SCRIPTS_DIR = Path(__file__).parent
ROOT_DIR = SCRIPTS_DIR.parent
SRC_DIR = ROOT_DIR / 'src'


if __name__ == '__main__':
    process = subprocess.Popen(
        ['flake8', str(SRC_DIR.absolute()), str(SCRIPTS_DIR)],
    )
    process.communicate()
    exit(process.returncode)
