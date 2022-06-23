import clone_monkeypatch
from pathlib import Path
from . import include, custom_tags, style
from .shared import HtmlpException, htmlBeautifulSoup

def compile(path: str, include_dir: str, minify: bool=False) -> (str, set[Path]):
    with open(path) as file:
        read_file = file.read()
    dom = htmlBeautifulSoup(read_file)
    include.compile(dom, include_dir)
    style.compile(dom, minify=minify)
    custom_tags.compile(dom)
    return dom.prettify()
