import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

def wait_modify(path):
    observer = Observer()
    event_handler = FileSystemEventHandler()
    event_handler.on_modified = lambda _: observer.stop()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    observer.join()