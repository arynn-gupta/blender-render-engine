import streamlit as st
import mimetypes
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
import datetime as dt
import os, shutil
from itertools import cycle
import lib.dummy
from lib.utils import styling

class Watchdog(FileSystemEventHandler):
    def __init__(self, hook):
        self.hook = hook

    def on_any_event(self, event):
        self.hook()

def update_dummy_module():
    dummy_path = "lib/dummy.py"
    with open(dummy_path, "w") as fp:
        fp.write(f'timestamp = "{dt.datetime.now()}"')

def install_monitor():
    observer = Observer()
    observer.schedule(
        Watchdog(update_dummy_module),
        path="output/",
        recursive=True)
    observer.start()

def main():
    styling()

    st.title("Output")

    
    if (os.path.isdir("output")):

        if not "monitor_filesystem" in st.session_state:
            st.session_state["monitor_filesystem"] = "running"
            install_monitor()

        if "rendering" in st.session_state :
            st.success("Rendering...")

        if not len(os.listdir('output')) == 0:
            output = "XRender-Output"
            output_file_name = output + ".zip"
            if os.path.exists(output_file_name):
                os.remove(output_file_name)
            shutil.make_archive(output, 'zip', "output")
            with open(f"{output_file_name}", "rb") as file:
                st.download_button(
                        label="Download Zip",
                        data=file,
                        file_name=f"{output_file_name}",
                        mime="application/zip"
                    )

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