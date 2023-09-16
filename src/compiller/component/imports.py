from dataclasses import dataclass
from pathlib import Path
from ..Source import Source
from .. import exceptions as ex
from typing import Callable, Dict, List, TypeAlias, cast, Self
from functools import cached_property
from bs4 import ResultSet, Tag


@dataclass(init=True, unsafe_hash=True)
class ComponentArgDefinition:
    declaration: str
    default_value: str | None = None

    @cached_property
    def is_optional(self) -> bool:
        return self.declaration.startswith('?')

    @cached_property
    def name(self) -> str:
        if self.is_optional:
            return self.declaration[1:]
        else:
            return self.declaration


@dataclass(frozen=True)
class ComponentDefinition:
    file: Path
    imports: Dict[str, Self]
    style_prefix: str
    template: Tag | None
    args_def: List[ComponentArgDefinition]
    script: str
    stylesheet: str

    def get_global_css_class_name(self, local_css_class_name: str) -> str:
        return self.style_prefix + local_css_class_name


Imports: TypeAlias = Dict[str, ComponentDefinition]


def parse_imports_and_remove_them(
    source: Source,
    include_dir: Path,
    route: List[Path] | None = None,
) -> Imports:
    if route is None:
        route = [source.path]
    ensure_no_recursion(route)

    imports: Imports = dict()
    for tag in source.tag.select('import'):
        if 'path' not in tag.attrs.keys():
            raise ex.NoRequiredAttr(
                'path', 'import', route[-1], tag.sourceline
            )
        path = include_dir / cast(str, tag['path'])

        alias = tag.attrs.get('alias', path.stem).lower()
        if alias in imports.keys():
            raise ex.SameImportAliases(alias, source.path)
        route.append(path)
        imports[alias] = _parse_definition(
            Source(source.path, tag),
            path,
            lambda src: parse_imports_and_remove_them(src, include_dir, route)
        )
        route.pop()
        tag.decompose()
    return imports


def ensure_no_recursion(route: List[Path]) -> None:
    if len(route) == 0:
        return
    if route.index(route[-1]) != len(route) - 1:
        raise ex.ImportRecursion(route)


_cache_by_path: Dict[Path, ComponentDefinition] = dict()


def _parse_definition(
    src: Source,
    path: Path,
    parse_imports: Callable[[Source], Imports],
) -> ComponentDefinition:
    if path not in _cache_by_path.keys():
        if not path.exists():
            raise ex.ImportedFileNotFound(path, src.path, src.tag.sourceline)
        source = Source(path)
        _check_for_disallowed_toplevel_tags(source)
        imports = parse_imports(source)
        style_prefix: str = _pick_style_prefix(path)
        _cache_by_path[path] = ComponentDefinition(
            path,
            imports,
            style_prefix,
            _pick_template(source),
            _pick_args_def(source),
            _pick_script(source),
            _pick_stylesheet(source),
        )
    return _cache_by_path[path]


def _check_for_disallowed_toplevel_tags(src: Source) -> None:
    allowed = ['template', 'style', 'scripts', 'import']
    for tag in src.tag.find_all(recursive=False):
        if tag.name not in allowed:
            raise ex.ProhibitedTopLevelTag(tag, src.path)


def _pick_style_prefix(path_to_file: Path) -> str:
    return path_to_file.stem


def _pick_stylesheet(src: Source) -> str:
    styles: ResultSet[Tag] = src.tag.find_all('style')
    if len(styles) > 1:
        raise ex.MultipleTopLevelTags(styles, src.path)
    if len(styles) == 0:
        return ''
    return styles[0].decode_contents()


def _pick_args_def(src: Source) -> List[ComponentArgDefinition]:
    template = cast(Tag, src.tag.find('template', recursive=False))
    if template is None:
        return []
    args = str(template.get('args', '')).split()
    defs = list(map(ComponentArgDefinition, args))
    for d in defs:
        if d.name == "children":
            raise ex.NoChildrenArg(src.path, template.sourceline)
    return defs


def _pick_template(src: Source) -> Tag | None:
    templates = src.tag.select('template')
    if len(templates) > 1:
        raise ex.MultipleTopLevelTags(templates, src.path)
    if len(templates) == 0:
        return None
    return templates[0]


def _pick_script(src: Source) -> str:
    scripts = src.tag.select('script')
    if len(scripts) > 1:
        raise ex.MultipleTopLevelTags(scripts, src.path)
    if len(scripts) == 0:
        return ''
    return scripts[0].decode_contents()
