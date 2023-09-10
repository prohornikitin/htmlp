from copy import deepcopy
from dataclasses import dataclass
from functools import cached_property
import re
from typing import Dict, Iterable, List, cast
from bs4 import PageElement, Tag
from .uniques import UniquesPerComponentInstance

from .imports import ComponentArgDefinition, ComponentDefinition, Imports
from ..shared import HtmlpException

@dataclass(init=False, unsafe_hash=True)
class ComponentArg(ComponentArgDefinition):
    value: str|None

    def __init__(self, declarationOrDef: str, default_value: str|None=None, value: str|None=None):
        super().__init__(declarationOrDef, default_value)
        if value is None:
            self.value = default_value
        else:
            self.value = value
        
        if (self.value is None) and not self.is_optional:
            raise HtmlpException(f"Non-optional component's attribute '{self.name}' has no value")
    
    @staticmethod
    def from_definition(definition: ComponentArgDefinition, value: str|None):
        return ComponentArg(definition.declaration, definition.default_value, value)
    
    @cached_property
    def placeholder(self):
        return '$'+ self.name

    @cached_property
    def unique_placeholder(self):
        return '!' + self.name

    def substitute_in(self, string: str):
        if self.value is None:
            return string.replace(self.placeholder, '')
        else:
            return string.replace(self.placeholder, self.value).replace(self.unique_placeholder, self.value)

def substitute_components(imports: Imports, where: Tag):
    for [alias, definition] in imports.items():
        if where.name == alias:
            _substitute_one(definition, where)
            continue
        for usage in where.find_all(alias):
            _substitute_one(definition, usage)

def _substitute_one(component: ComponentDefinition, usage: Tag):
    fictitious_root = generate_html(component, usage.attrs, usage.children)
    if fictitious_root is None:
        usage.decompose()
        return
    
    last_tag: PageElement = usage
    for tag in deepcopy(fictitious_root.children):
        last_tag.insert_after(tag)
        last_tag = tag
    usage.decompose()


def generate_html(definition: ComponentDefinition, attributes: Dict[str, str], children: Iterable[PageElement]) -> Tag|None:
    template = deepcopy(definition.template)
    if template is None:
        return None
    _apply_args(template, definition.args_def, attributes)
    _apply_uniques(template)
    _substitute_inner_components(template, cast(Imports, definition.imports))
    _insert_children(template, children)
    return template

def _apply_args(template: Tag, definitions: Iterable[ComponentArgDefinition], values: Dict[str, str]):
    names = set(map(lambda d: d.name, definitions))
    extra = set(values.keys()).difference(names)
    if len(extra) > 0:
        raise HtmlpException(f"Extra arguments [{','.join(extra)}]", template.sourceline)

    args: Iterable[ComponentArg] = set(map(
        lambda d: ComponentArg.from_definition(d, values.get(d.name)),
        definitions,
    ))
    for tag in template.find_all():
        for [name, value] in tag.attrs.copy().items():
            for arg in list(args):
                if arg.placeholder == name:
                    del tag[name]
                    if(arg.value is not None):
                        tag[arg.name] = arg.value
                    break
                value = arg.substitute_in(value)
                if value.isspace() or value == '':
                    del tag[name]
                    break
                else:
                    tag[name] = value

def _substitute_inner_components(template: Tag, imports: Imports):
    substitute_components(cast(Imports, imports), template)

def _insert_children(template: Tag, children: Iterable[PageElement]):
    placeholder_regex = re.compile("\s*\$children\s*")
    for tag in template.find_all(string=placeholder_regex):
        last_child = tag
        for child in deepcopy(children):
            last_child.insert_after(child)
            last_child = child
        tag.extract()

def _apply_uniques(template: Tag):
    uniques = UniquesPerComponentInstance()
    unique_id_pattern = re.compile('![A-z]+\s|![A-z_-]+$')
    for tag in template.find_all():
        for [name, value] in tag.attrs.copy().items():
            for id in unique_id_pattern.findall(value):
                value = value.replace(id, uniques.get_by_id(id))
            tag[name] = value