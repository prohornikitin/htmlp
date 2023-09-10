from pathlib import Path
import subprocess
import os


ROOT_DIR = Path(__file__).parent.parent
SRC_DIR = ROOT_DIR / 'src'

if __name__ == '__main__':
    env = os.environ.copy()
    env['MYPYPATH'] = str(SRC_DIR.absolute())
    subprocess.Popen(
        ['mypy', '--explicit-package-bases', str(SRC_DIR.absolute())],
        env=env,
    ).communicate()
    
