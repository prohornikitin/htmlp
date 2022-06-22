from pathlib import Path
from functools import reduce
from .shared import HtmlpException, htmlBeautifulSoup

def compile(dom, include_dir, route=None):
    if route is None:
        route = []

    for tag in dom.select('include'):
        if 'ref' not in tag.attrs.keys():
            raise HtmlpException(f"Can't find 'ref' attribute of <include/> at line {tag.sourceline} of {route[-1]}.")
        
        ref = tag['ref']
        included_dom = try_parse_file(Path(include_dir) / ref)
        tag.replace_with(included_dom)

        ensure_no_recursion(route, ref)
        route.append(ref)
        compile(included_dom, include_dir, route)
        route.pop()

def try_parse_file(path: Path):
    try:
        with open(path) as file:
            text = file.read()
    except FileNotFoundError:
        raise HtmlpException(f"Can't open file '{path}'. File not found.")
    except PermissionError:
        raise HtmlpException(f"Can't open file '{path}'. Permission error.")
    except OSError:
        raise HtmlpException(f"Can't open file '{path}'.")
    return htmlBeautifulSoup(text)

def ensure_no_recursion(route, current_file):
    if current_file in route:
        route.append(current_file)
        formatted_route = reduce(lambda acc, x: f'{acc} -> {x}', route);
        raise HtmlpException(f"Include recursion. Route: {formatted_route}")