from pathlib import Path
from typing import Iterable

class HtmlpException(Exception):
	def __init__(self, error: str, source_lines: None|int|Iterable[int] = None, file_path: Path|None = None):
		if source_lines is None:
			super().__init__(error)
			return
		if isinstance(source_lines, int):
			if file_path is None:
				super().__init__(f"{error}. Line {source_lines}")
			else:
				super().__init__(f"{error}. Line {source_lines} of file {file_path}")
		else:
			lines = ','.join(map(str, source_lines))
			if file_path is None:
				super().__init__(f"{error}. Lines: {lines}")
			else:
				super().__init__(f"{error}. Lines {lines} of file {file_path}")
