from xml.dom import minidom
import xml.dom
import argparse
import os
import time
import traceback
import sass


def main():
    args = parse_args()
    if not args.watch:
        with minidom.parse(args.input_file[0]) as dom:
            compile(dom)
            with open(args.output_file, 'w') as file:
                dom.writexml(file)
    else:
        while(True):
            try:
                wait_file_modified(args.input_file[0])
                with minidom.parse(args.input_file[0]) as dom:
                    compile(dom)
                    with open(args.output_file, 'w') as file:
                        dom.writexml(file)
            except KeyboardInterrupt:
                break

def parse_args():
    parser = argparse.ArgumentParser(description='Doing something')
    parser.add_argument('input_file', type=str, nargs=1,
                        help='an input file')
    parser.add_argument('output_file', type=str, nargs='?', default='output.html',
                        help='an input file')
    parser.add_argument('--watch', action='store_const',
                        const=True, default=False,
                        help='watch files and recompile when they change')
    return parser.parse_args()


def wait_file_modified(file_path):
    modified = modified_on = os.path.getmtime(file_path)
    while modified <= modified_on :
        time.sleep(0.5)
        modified = os.path.getmtime(file_path)


def compile(dom):
    compile_imports(dom)
    compile_styles(dom)
    compile_custom_tags(dom)

def compile_imports(dom):
    for node in dom.getElementsByTagName('import'):
        path = node.getAttribute("ref")
        with minidom.parse(path) as embedde_dom:
            root = embedde_dom.documentElement.cloneNode(deep=True)
            node.parentNode.replaceChild(root, node)

def compile_styles(dom):
    for style in dom.getElementsByTagName('style'):
        style.childNodes[0].data = sass.compile(string=style.childNodes[0].data, indented=True)

def compile_custom_tags(dom):
    defs = dom.getElementsByTagName('def')
    defs_tag_names = list(map(lambda x: x.getAttribute('tag'), defs))
    def_cloner = DefCloner(dom)
    for i in range(len(defs_tag_names)):
        tag_name = defs_tag_names[i]
        for tag in dom.getElementsByTagName(tag_name):
            tag.parentNode.replaceChild(def_cloner.clone(defs[i]), tag)

    for d in defs:
        d.parentNode.removeChild(d)



class DefCloner:
    def __init__(self, dom):
        self.dom = dom
        self.ids = dict()
        self.max_id = 0

    def clone(self, def_node):
        element = self.dom.createElement(def_node.getAttribute('tag'))
        for tag in def_node.childNodes:
            clone = tag.cloneNode(deep=True)
            self._modify_def_node(clone)
            element.appendChild(clone)
        return element

    def _modify_def_node(self, node):
        if node.nodeType != xml.dom.Node.ELEMENT_NODE:
            return

        if node.hasAttribute('id'):
            old = node.getAttribute('id')
            if self.ids.get(old) is None:
                self.max_id += 1
                self.ids[old] = str(self.max_id)
            node.setAttribute('id', self.ids[old])

        if node.hasAttribute('for'):
            old = node.getAttribute('for')
            if self.ids.get(old) is None:
                self.max_id += 1
                self.ids[old] = str(self.max_id)
            node.setAttribute('for', self.ids[old])

        for child in node.childNodes:
            self._modify_def_node(child)



if __name__ == '__main__':
    main()