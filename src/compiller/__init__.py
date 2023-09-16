from pathlib import Path
from .component.imports import (
    parse_imports_and_remove_them,
    clear_imports_cache,
)
from .component.gen import substitute_components
from .component.uniques import restart_uniques_generator
from .exceptions import HtmlpException
from .Source import Source


def process_file(path: Path, include_dir: Path) -> str:
    clear_imports_cache()
    restart_uniques_generator()
    src = Source(path)
    imports = parse_imports_and_remove_them(src, include_dir)
    substitute_components(imports, src)
    return str(src.tag)


__all__ = [
    'HtmlpException',
    'process_file'
]
