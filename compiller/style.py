def compile(dom):
    data = ''
    for style in dom.select('style'):
        data += '\n'
        data += style.text
        style.decompose()
    overall = dom.new_tag('style')
    overall.string = data
    dom.html.head.insert(1,overall)