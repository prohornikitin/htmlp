
from pathlib import Path
from typing import Iterable, List, Never, Set
from os import getcwd
from bs4 import Tag


def _assemble_location_string(
    file: Path | None,
    line: int | None = None
) -> str:
    if file is None:
        return 'Error'
    if line is None:
        line1 = 'Unknown'
    else:
        line1 = str(line)
    return f"Error in file {file.relative_to(getcwd())}, on line {line1}"


class HtmlpException(Exception):
    file: Path | None
    line: int | None
    msg: str

    def __init__(
        self,
        *sentences: str,
        file: Path | None = None,
        line: int | None = None
    ):
        self.file = file
        self.line = line
        self.msg = '. '.join(sentences)
        text = _assemble_location_string(file, line) + ':\n' + self.msg + '.'
        super().__init__(text)


def add_location_context(
    e: HtmlpException,
    file: Path | None = None,
    line: int | None = None
) -> Never:
    if file is None:
        file = e.file
    if line is None:
        line = e.line
    raise HtmlpException(
        e.msg,
        file=file,
        line=line,
    )


class NoChildrenArg(HtmlpException):
    def __init__(self, file: Path | None = None, line: int | None = None):
        super().__init__(
            "'children' can't be used as an argument of component",
            "It's reserved for inner children (suddenly)",
            file=file,
            line=line,
        )


class ImportRecursion(HtmlpException):
    def __init__(self, route: Iterable[Path]):
        formatted_route: str = ' -> \n\t'.join(
            map(lambda x: str(x.relative_to(getcwd())), route)
        )
        super().__init__(
            'Import recursion',
            "Route:\n" + formatted_route,
        )


class NoRequiredAttr(HtmlpException):
    def __init__(
        self,
        tag: str,
        attr: str,
        file: Path | None = None,
        line: int | None = None,
    ):
        super().__init__(
            f"Can't find '{attr}' attribute of <{tag}/>",
            file=file,
            line=line,
        )


class SameImportAliases(HtmlpException):
    def __init__(self, alias: str, file: Path):
        super().__init__(
            f"Can't use same alias {alias} on different imports in the same file",  # noqa: E501
            file=file,
        )


class ImportedFileNotFound(HtmlpException):
    def __init__(
        self,
        imported: Path,
        source: Path,
        source_line: int | None = None
    ):
        super().__init__(
            f"Cannot import component from non-existant file {imported}",
            line=source_line,
            file=source,
        )


class ProhibitedTopLevelTag(HtmlpException):
    def __init__(self, tag: Tag, file: Path):
        super().__init__(
            f"Tag <{tag.name}> is not allowed at top-level",
            file=file,
            line=tag.sourceline,
        )


class MultipleTopLevelTags(HtmlpException):
    def __init__(self, tags: List[Tag], file: Path):
        lines = ','.join(map(lambda s: str(s.sourceline), tags))
        tag = tags[0].name
        super().__init__(
            f"Multiple <{tag}> tags are not allowed within single component",
            f"Lines: {lines}",
            file=file,
        )


class ExtraArgs(HtmlpException):
    def __init__(
        self,
        extra_args: Set[str],
        file: Path,
        line: int | None = None
    ):
        formatted_extra_args = ','.join(
            map(lambda a: f"'{a}'", extra_args)
        )
        if len(extra_args) == 1:
            msg = f"Extra argument {formatted_extra_args}"
        else:
            msg = f"Extra arguments: [{formatted_extra_args}]"
        super().__init__(
            msg,
            file=file,
            line=line,
        )
