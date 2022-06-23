from .shared import HtmlpException


def compile(dom):
    defs = dom.select('def')
    for definition in defs:
        CustomTagsCompiller(dom, definition).compile()
        definition.decompose()

class CustomTagsCompiller:
    class _Arg:
        def __init__(self, arg_str):
            if arg_str.startswith('!'):
                self.optional = True
                self.name = arg_str[1:]
            else:
                self.optional = False
                self.name = arg_str
            self.template = '$' + self.name


    def __init__(self, dom, def_node):
        self._dom = dom
        self._max_id = 0
        self._def = def_node
        if self._def.get('tag') is None:
            raise HtmlpException(f"Can't find 'tag' attribute of <def/> at line {self._def.sourceline}.")
        if self._def.get('tag').strip() == '':
            raise HtmlpException(f"Empty 'tag' attribute of <def/> at line {self._def.sourceline}.")
        self._args = list(map(self._Arg, self._def.get('args', default='').split()))
        
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
        for arg in self._args:
            if (arg.name not in src.attrs.keys()) and not arg.optional:
                raise HtmlpException(f"expected attribute '{arg.name}' for <{src.name}/> at line {src.sourceline}")

        for (k,v) in dest.attrs.copy().items():
            for arg in self._args:
                if k == arg.template:
                    if not (arg.optional and src.get(arg.name) is None):
                        dest[arg.name] = dest[k] if (dest[k] != '') else None
                    del dest[k]
                elif v.find(arg.template) != (-1):
                    if arg.optional and (src.get(arg.name) is None):
                        v = v.replace(arg.template, '')
                    else:
                        v = v.replace(arg.template, src[arg.name])
                    if v.isspace() or v == '':
                        del dest[k]
                    else:
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