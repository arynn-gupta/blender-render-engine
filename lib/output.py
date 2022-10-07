from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
import datetime as dt
import lib.dummy
from lib.utils import render_output
import streamlit as st

class Watchdog(FileSystemEventHandler):
    def __init__(self, hook):
        self.hook = hook

    def on_any_event(self, event):
        self.hook()

def update_dummy_module():
    dummy_path = "lib/dummy.py"
    with open(dummy_path, "w") as fp:
        fp.write(f'timestamp = "{dt.datetime.now()}"')

@st.cache
def install_monitor():
    observer = Observer()
    observer.schedule(
        Watchdog(update_dummy_module),
        path="output/",
        recursive=True)
    observer.start()

def output():
    try:
        install_monitor()
        render_output()
    except :
        pass