import streamlit as st
import mimetypes
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
import datetime as dt
import os
from itertools import cycle
from lib.utils import styling, sidebar, make_zip
import lib.dummy

class Watchdog(FileSystemEventHandler):
    def __init__(self, hook):
        self.hook = hook

    def on_any_event(self, event):
        self.hook()

def update_dummy_module():
    dummy_path = "lib/dummy.py"
    file = open(dummy_path, "w")
    file.write(f'timestamp = "{dt.datetime.now()}"')
    file.close()

def install_monitor():
    observer = Observer()
    observer.schedule(
        Watchdog(update_dummy_module),
        path="output/",
        recursive=True)
    observer.start()

def main():
    styling()
    sidebar()

    st.title("Output")

    
    if os.path.exists("output"):

        if "monitor_filesystem" not in st.session_state:
            st.session_state["monitor_filesystem"] = "running"
            install_monitor()

        col1, col2 = st.columns(2)
        col1.button("Make Zip", disabled= len(os.listdir("output"))==0, on_click = make_zip, args = ("output", col2))

        mimetypes.init()
        images=[]
        videos=[]
        for filename in os.listdir("output"):
            mimestart = mimetypes.guess_type(filename)[0]
            if mimestart != None:
                mimestart = mimestart.split('/')[0]
                if mimestart in ['image']:
                    images.append(os.path.join("output", filename))
                if mimestart in ['video']:
                    videos.append(os.path.join("output", filename))
        cols = cycle(st.columns(3))
        for idx, image in enumerate(images):
            next(cols).image(image)
        for idx, video in enumerate(videos):
            next(cols).video(video)


if __name__ == '__main__':
    main()