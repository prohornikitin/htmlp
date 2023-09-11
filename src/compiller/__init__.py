from pathlib import Path

from .component.imports import parse_imports_and_remove_them
from .component.gen import substitute_components
from .HtmlpException import HtmlpException
from .utils import htmlBeautifulSoup

def process_file(path: Path, include_dir: Path) -> str:
    with open(path) as file:
        read_file = file.read()
    dom = htmlBeautifulSoup(read_file)
    imports = parse_imports_and_remove_them(dom, include_dir)
    substitute_components(imports, dom)
    return str(dom)
