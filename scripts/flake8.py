#!/usr/bin/env python
from pathlib import Path
import subprocess


ROOT_DIR = Path(__file__).parent.parent
SRC_DIR = ROOT_DIR / 'src'

if __name__ == '__main__':
    subprocess.Popen(
        ['flake8', str(SRC_DIR.absolute())],
    ).communicate()
