from pathlib import Path
from typing import Iterable


class HtmlpException(Exception):
    def __init__(
        self,
        error: str,
        source_lines: None | int | Iterable[int] = None,
        file_path: Path | None = None
    ):
        if source_lines is None:
            text = error
        elif isinstance(source_lines, int):
            if file_path is None:
                text = f"{error}. Line {source_lines}"
            else:
                text = f"{error}. Line {source_lines} of file {file_path}"
        else:
            lines = ','.join(map(str, source_lines))
            if file_path is None:
                text = f"{error}. Lines: {lines}"
            else:
                text = f"{error}. Lines {lines} of file {file_path}"
        super().__init__(text)
