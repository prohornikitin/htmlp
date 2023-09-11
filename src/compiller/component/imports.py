from dataclasses import dataclass
from pathlib import Path
from functools import reduce
from ..HtmlpException import HtmlpException
from ..utils import htmlBeautifulSoup
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, List, TypeAlias, cast, Self
from functools import cached_property
from bs4 import BeautifulSoup, ResultSet, Tag

@dataclass(init=False)
class ComponentArgDefinition:
	declaration: str
	default_value: str|None

	def __init__(self, declaration: str, default_value: str|None=None):
		if declaration in ["children", '?children']:
			raise HtmlpException("You can't use 'children' as an argument. It's reserved for inner children (suddenly).")
		self.declaration = declaration
		self.default_value = default_value #For futute use

	@cached_property
	def is_optional(self):
		return self.declaration.startswith('?')
	
	@cached_property
	def name(self):
		if self.is_optional:
			return self.declaration[1:]
		else:
			return self.declaration


@dataclass(frozen=True)
class ComponentDefinition:
	style_prefix: str
	stylesheet: str
	args_def: List[ComponentArgDefinition]
	template: Tag|None
	script: str
	imports: Dict[str, Self]
	

	def get_global_css_class_name(self, local_css_class_name: str) -> str:
		return self.style_prefix + local_css_class_name

Imports: TypeAlias = Dict[str, ComponentDefinition]

def parse_imports_and_remove_them(dom: BeautifulSoup, include_dir: Path, route=None) -> Imports:
	if route is None:
		route = []
	ensure_no_recursion(route)
	
	imports: Imports = dict()
	for tag in dom.select('import'):
		if 'path' not in tag.attrs.keys():
			raise HtmlpException(f"Can't find 'path' attribute of <import/> at line {tag.sourceline} of {route[-1]}.")
		path = include_dir / cast(str, tag['path'])
		
		alias = tag.attrs.get('alias', path.stem).lower()
		if alias in imports.keys():
			raise HtmlpException(f"Can't use same alias {alias} on different imports at {tag.sourceline} of {route[-1]}.")
		route.append(path)
		imports[alias] = parse_definition(path, lambda dom: parse_imports_and_remove_them(dom, include_dir, route))
		route.pop()
		tag.decompose()
	return imports


def ensure_no_recursion(route: List[Path]):
	if len(route) == 0:
		return
	if route.index(route[-1]) != len(route) - 1:
		formatted_route = reduce(lambda acc, x: f'{acc} -> {x}', route) # type: ignore
		raise HtmlpException(f"Import recursion. Route: {formatted_route}")


_cache_by_path: Dict[Path, ComponentDefinition] = dict()

def parse_definition(
		path: Path, 
		parse_imports: Callable[[BeautifulSoup], Imports]
) -> ComponentDefinition:
	if path not in _cache_by_path.keys():
		if not path.exists():
			raise HtmlpException(f"Cannot import component non-existant file {path.absolute()}")
		with open(path) as file:
			dom = htmlBeautifulSoup(file.read())
		_check_for_disallowed_toplevel_tags(dom, path)
		imports = parse_imports(dom)
		style_prefix: str = _pick_style_prefix(path)
		_cache_by_path[path] = ComponentDefinition(
			imports = imports,
			style_prefix = style_prefix,
			template = _pick_template(dom),
			args_def = _pick_args_def(dom),
			script = _pick_script(dom),
			stylesheet = _pick_stylesheet(dom),
		)
	return _cache_by_path[path]


def _check_for_disallowed_toplevel_tags(dom: BeautifulSoup, file_path: Path):
	allowed = ['template', 'style', 'scripts', 'import']
	for tag in dom.find_all(recursive=False):
		if tag.name not in allowed:
			raise HtmlpException(f"Tag <{tag.name}> is not allowed at top-level", tag.sourceline, file_path)
		
def _pick_style_prefix(path_to_file: Path) -> str:
	return path_to_file.stem

def _pick_stylesheet(dom: BeautifulSoup) -> str:
	styles: ResultSet[Tag] = dom.find_all('style')
	if len(styles) > 1:
		lines = ','.join(map(lambda s: s.sourcesline, styles)) # type: ignore
		raise HtmlpException(f"Multiple <style> tags are not allowed within single component. Lines: {lines}")
	if len(styles) == 0:
		return ''
	return styles[0].decode_contents()

def _pick_args_def(dom: BeautifulSoup) -> List[ComponentArgDefinition]:
	template = cast(Tag, dom.find('template', recursive=False))
	if template is None:
		return []
	args = str(template.get('args', '')).split()
	return list(map(ComponentArgDefinition, args)) # type: ignore


def _pick_template(dom: BeautifulSoup) -> Tag|None:
	templates = dom.select('template')
	if len(templates) > 1:
		lines = ','.join(map(lambda s: s.sourcesline, templates)) # type: ignore
		raise HtmlpException(f"Multiple <template> tags are not allowed within single component. Lines: {lines}")
	if len(templates) == 0:
		return None
	return templates[0]

def _pick_script(dom: BeautifulSoup) -> str:
	scripts = dom.select('script')
	if len(scripts) > 1:
		lines = ','.join(map(lambda s: s.sourcesline, scripts)) # type: ignore
		raise HtmlpException(f"Multiple <script> tags are not allowed within single component. Lines: {lines}")
	if len(scripts) == 0:
		return ''
	return scripts[0].decode_contents()
