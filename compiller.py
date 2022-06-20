import clone_monkeypatch
from bs4 import BeautifulSoup

def compile(path: str) -> str:
    with open(path) as file:
        dom = BeautifulSoup(file.read(), 'html.parser')
    compile_imports(dom)
    compile_styles(dom)
    compile_custom_tags(dom)

    return dom.prettify()

def compile_imports(dom):
    for node in dom.select('include'):
        with open(node["ref"]) as file:
            text = file.read()
        include_html = BeautifulSoup(text, 'html.parser')
        node.replace_with(include_html)

def compile_styles(dom):
    data = ''
    for style in dom.select('style'):
        data += '\n'
        data += style.text
        style.decompose()
    overall = dom.new_tag('style')
    overall.string = data
    dom.html.insert(1,overall)

def compile_custom_tags(dom):
    defs = dom.select('def')
    for definition in defs:
        CustomElementsCompiller(dom, definition).compile()
        definition.decompose()



class CustomElementsCompiller:
    def __init__(self, dom, def_node):
        self._dom = dom
        self._max_id = 0
        self._def = def_node

    def compile(self):
        for tag in self._dom.select(self._def['tag']):
            self._compile_one(tag)

    def _compile_one(self, tag):
        self.ids = dict()
        for c in self._def.findChildren():
            child = c.clone()
            self._fix_id_collision(child)
            child = self._apply_args(tag, child)
            tag.insert_after(child)
        tag.decompose()


    def _apply_args(self, src, dest):
        dest = dest.prettify()
        args = self._def.get('args', default='').split()
        for arg in args:
            value = src[arg]
            if arg == 'class':
                value = " ".join(value)
            dest = dest.replace(f'${arg}', value)
        dest = dest.replace('$children', src.decode_contents(), 1)
        return BeautifulSoup(dest, 'html.parser')

    def _fix_id_collision(self, node):
        if node.get('id') and node.get('id').startswith('?'):
            old = node['id']
            if self.ids.get(old) is None:
                self._max_id += 1
                self.ids[old] = str(self._max_id)
            node['id'] = self.ids[old]

        if node.get('for') and node.get('for').startswith('?'):
            old = node['for']
            if self.ids.get(old) is None:
                self._max_id += 1
                self.ids[old] = str(self._max_id)
            node['for'] = self.ids[old]

        for child in node.findChildren():
            self._fix_id_collision(child)
