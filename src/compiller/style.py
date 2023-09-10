def compile(dom):
	no_script = ""
	for tag in dom.select('noscript style'):
		no_script += '\n'
		no_script += tag.text
		parent = tag.parent
		tag.decompose()
		if parent.name == 'noscript' and (parent.find() is None):
			parent.decompose()
	overall = ""
	for tag in dom.select('style'):
		overall += '\n'
		overall += tag.text
		tag.decompose()

	if no_script.strip() != '':
		noscript = dom.new_tag("noscript")
		noscript.append(dom.new_tag("style"))
		noscript.style.string = no_script
		dom.html.head.append(noscript)
	if overall.strip() != '':
		style = dom.new_tag("style")
		dom.html.head.append(style)
