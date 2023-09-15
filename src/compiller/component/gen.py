from copy import deepcopy
from dataclasses import dataclass
from functools import cached_property
from pathlib import Path
import re
from typing import cast
from bs4 import PageElement, Tag

from compiller.Source import Source
from .uniques import UniquesPerComponent
from .imports import ComponentArgDefinition, ComponentDefinition, Imports
from .. import exceptions as ex


@dataclass(init=False, unsafe_hash=True)
class ComponentArg:
    _def: ComponentArgDefinition
    value: str | None

    def __init__(
        self,
        tag_name: str,
        definiton: ComponentArgDefinition,
        value: str | None = None
    ) -> None:
        self._def = definiton
        if value is None:
            self.value = definiton.default_value
        else:
            self.value = value
        if (self.value is None) and not self.is_optional:
            raise ex.NoRequiredAttr(tag_name, self.name)

    @cached_property
    def is_optional(self) -> bool:
        return self._def.is_optional

    @cached_property
    def name(self) -> str:
        return self._def.name

    @cached_property
    def placeholder(self) -> str:
        return '$' + self.name

    @cached_property
    def _unique_placeholder(self) -> str:
        return '!' + self.name

    def substitute_in(self, string: str) -> str:
        if self.value is None:
            return string.replace(self.placeholder, '')
        else:
            return string.replace(
                self.placeholder, self.value
            ).replace(
                self._unique_placeholder, self.value
            )


def substitute_components(imports: Imports, usage: Source) -> None:
    for [alias, definition] in imports.items():
        if usage.tag.name == alias:
            _substitute_one(definition, usage)
            continue
        for tag in usage.tag.find_all(alias):
            _substitute_one(definition, Source(usage.path, tag))


def _substitute_one(component_def: ComponentDefinition, usage: Source) -> None:
    component = Component(component_def, usage)
    fictitious_root = component.generate_html()
    if fictitious_root is None:
        usage.tag.decompose()
        return
    last_tag: PageElement = usage.tag
    for tag in deepcopy(fictitious_root.children):
        last_tag.insert_after(tag)
        last_tag = tag
    usage.tag.decompose()


class Component:
    _html: Tag
    _def: ComponentDefinition
    _usage: Tag
    _usage_file: Path
    _uniques: UniquesPerComponent

    def __init__(
        self,
        definition: ComponentDefinition,
        usage_src: Source,
    ) -> None:
        self._uniques = UniquesPerComponent()
        self._def = definition
        self._usage = usage_src.tag
        self._usage_file = usage_src.path

    def generate_html(self) -> Tag | None:
        if self._def.template is None:
            return None
        self._html = deepcopy(self._def.template)
        self._apply_args()
        self._apply_uniques()
        self._substitute_inner_components()
        self._insert_children()
        return self._html

    def _apply_args(self) -> None:
        values = self._usage.attrs
        names = set(map(lambda d: d.name, self._def.args_def))
        extra = set(values.keys()).difference(names)

        def arg_from_def(definition: ComponentArgDefinition):
            try:
                return ComponentArg(
                    self._usage.name,
                    definition,
                    self._usage.attrs.get(definition.name)
                )
            except ex.HtmlpException as e:
                ex.add_location_context(e, file=self._usage_file)

        if len(extra) > 0:
            raise ex.ExtraArgs(extra, self._usage_file, self._usage.sourceline)
        args = set(map(arg_from_def, self._def.args_def))
        for tag in self._html.find_all():
            for [name, value] in tag.attrs.copy().items():
                for arg in list(args):
                    if arg.placeholder == name:
                        del tag[name]
                        if arg.value is not None:
                            tag[arg.name] = arg.value
                        break
                    value = arg.substitute_in(value)
                    if value.isspace() or value == '':
                        del tag[name]
                        break
                    else:
                        tag[name] = value

    def _substitute_inner_components(self) -> None:
        imports = cast(Imports, self._def.imports)
        substitute_components(imports, Source(self._def.file, self._html))

    def _apply_uniques(self) -> None:
        unique_id_pattern = re.compile('![A-z]+\\s|![A-z_-]+$')
        for tag in self._html.find_all():
            for [name, value] in tag.attrs.copy().items():
                for id in unique_id_pattern.findall(value):
                    value = value.replace(id, self._uniques.get_by_id(id))
                tag[name] = value

    def _insert_children(self) -> None:
        children = self._usage.children
        placeholder_regex = re.compile("\\s*\\$children\\s*")
        for tag in self._html.find_all(string=placeholder_regex):
            last_child = tag
            for child in deepcopy(children):
                last_child.insert_after(child)
                last_child = child
            tag.extract()
