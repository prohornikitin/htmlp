from pathlib import Path
from typing import Iterable, TextIO
from compiller import process_file, HtmlpException
from minify_html import minify
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import sys
from args import Args, parse_args


def main(args: Args) -> None:
    if args.watch_dir is None:
        try:
            run_once(
                args.out,
                args.input,
                args.include_dir,
                args.need_minify,
            )
        except KeyboardInterrupt:
            return
        except HtmlpException:
            exit(1)
    else:
        run_with_watch(args)


def run_once(
    out: TextIO,
    input: Iterable[Path],
    include_dir: Path,
    need_minify: bool,
) -> None:
    for input_path in input:
        try:
            result = process_file(input_path, include_dir)
            if need_minify:
                result = minify(result)
            out.write(result)
        except HtmlpException as e:
            print(str(e),  file=sys.stderr)
            raise e


class Watcher(FileSystemEventHandler):
    def __init__(self, args: Args) -> None:
        super().__init__()
        self._args = args

    def on_modified(self):
        try:
            run_once(
                self._args.out,
                self._args.input,
                self._args.include_dir,
                self._args.need_minify,
            )
        except HtmlpException as e:
            print(str(e))


def run_with_watch(args: Args) -> None:
    observer = Observer()
    event_handler = Watcher(args)
    observer.schedule(event_handler, args.watch_dir, recursive=True)
    observer.start()
    try:
        observer.join()
    except KeyboardInterrupt:
        return


if __name__ == '__main__':
    try:
        main(parse_args())
    except KeyboardInterrupt:
        print()
