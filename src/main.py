from pathlib import Path
from typing import TextIO
from compiller import process_file, HtmlpException
from minify_html import minify
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent
import sys
from args import Args, parse_args


def main(args: Args) -> None:
    if args.watch_dir is not None:
        run_with_watch(args)
    else:
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


def run_once(
    out: TextIO,
    input: Path,
    include_dir: Path,
    need_minify: bool,
) -> None:
    try:
        if out.seekable():
            out.seek(0)
        result = process_file(input, include_dir)
        if need_minify:
            result = minify(result)
        out.write(result)
        out.flush()
    except HtmlpException as e:
        print(str(e),  file=sys.stderr)
        raise e


class Watcher(FileSystemEventHandler):
    def __init__(self, args: Args) -> None:
        super().__init__()
        self._args = args

    def on_modified(self, event: FileSystemEvent | None = None):
        if event is not None:
            print(f"File {event.src_path} was modified.")
        try:
            pass
            run_once(
                self._args.out,
                self._args.input,
                self._args.include_dir,
                self._args.need_minify,
            )
        except HtmlpException:
            pass  # Error has been printed to stderr already


def run_with_watch(args: Args) -> None:
    observer = Observer()
    event_handler = Watcher(args)
    event_handler.on_modified()
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
