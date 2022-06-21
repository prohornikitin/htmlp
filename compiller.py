import clone_monkeypatch
from bs4 import BeautifulSoup
from pathlib import Path
from functools import reduce


class HtmlpException(Exception):
    pass

def compile(path: str, include_dir: str) -> str:
    with open(path) as file:
        dom = BeautifulSoup(file.read(), 'html.parser', multi_valued_attributes=None)
    compile_imports(dom, include_dir)
    compile_styles(dom)
    compile_custom_tags(dom)

    return dom.prettify()

def compile_imports(dom, dir, route=[]):
    for tag in dom.select('include'):
        if tag.get('ref') is None:
            raise HtmlpException(f"Can't find 'ref' attribute of <include/> at line {tag.sourceline}.")
        ref = tag['ref']

        try:
            with open(Path(dir) / ref) as file:
                text = file.read()
        except FileNotFoundError:
            raise HtmlpException(f"Can't include file '{ref}'. File not found.")
        except PermissionError:
            raise HtmlpException(f"Can't include file '{ref}'. Permission error.")
        except OSError:
            raise HtmlpException(f"Can't include file '{ref}'.")

        included_dom = BeautifulSoup(text, 'html.parser', multi_valued_attributes=None)
        
        if route.count(ref) > 0:
            route.append(ref)
            formatted_route = reduce(lambda acc, x: f'{acc} -> {x}', route);
            raise HtmlpException(f"Include recursion. Route: {formatted_route}")

        route2 = route.copy()
        route2.append(ref)
        compile_imports(included_dom, dir, route2)
        tag.replace_with(included_dom)

def compile_styles(dom):
    data = ''
    for style in dom.select('style'):
        data += '\n'
        data += style.text
        style.decompose()
    overall = dom.new_tag('style')
    overall.string = data
    dom.html.head.insert(1,overall)

def compile_custom_tags(dom):
    defs = dom.select('def')
    for definition in defs:
        CustomTagsCompiller(dom, definition).compile()
        definition.decompose()



class CustomTagsCompiller:
    def __init__(self, dom, def_node):
        self._dom = dom
        self._max_id = 0
        self._def = def_node
        self._args = self._def.get('args', default='').split()
        if self._def.get('tag') is None:
            raise HtmlpException(f"Can't find 'tag' attribute of <def/> at line {self._def.sourceline}.")

    def compile(self):
        for tag in self._dom.select(self._def['tag']):
            self._compile_one(tag)

    def _compile_one(self, tag):
        self.ids = dict()
        for c in self._def.find_all(recursive=False):
            child = c.clone()
            self._fix_id_collision(child)
            self._insert_children(tag, child)
            self._apply_args(tag, child)
            tag.insert_after(child)
        tag.decompose()


    def _apply_args(self, src, dest):
        for k in self._args:
            if k not in src.attrs.keys():
                raise HtmlpException(f"expected attribute '{k}' for <{src.name}/> at line {src.sourceline}")
        for (k,v) in dest.attrs.items():
            for arg in self._args:
                v = v.replace('$'+arg, src[arg])
            dest[k] = v
        for child in dest.find_all(recursive=False):
            self._apply_args(src, child)

    def _insert_children(self, src, dest):
        if dest.text == '$children':
            dest.string = ""
            for child in src.find_all():
                dest.append(child)
            for child in src.find_all(text=True):
                dest.append(child)

        for tag in dest.find_all(recursive=False):
            self._insert_children(src, tag)


    def _fix_id_collision(self, tag):
        if tag.get('id') and tag.get('id').startswith('?'):
            old = tag['id']
            if self.ids.get(old) is None:
                self._max_id += 1
                self.ids[old] = str(self._max_id)
            tag['id'] = self.ids[old]

        if tag.get('for') and tag.get('for').startswith('?'):
            old = tag['for']
            if self.ids.get(old) is None:
                self._max_id += 1
                self.ids[old] = str(self._max_id)
            tag['for'] = self.ids[old]

        for child in tag.find_all(recursive=False):
            self._fix_id_collision(child)
