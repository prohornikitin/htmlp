from pathlib import Path
from bs4 import BeautifulSoup, Tag


class Source:
    path: Path
    tag: Tag

    def __init__(self, path: Path, tag: Tag | None = None) -> None:
        self.path = path
        if tag is not None:
            self.tag = tag
            return
        with open(path) as file:
            self.tag = BeautifulSoup(
                file.read(),
                'html.parser',
                multi_valued_attributes=None,
            )
