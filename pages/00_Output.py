import streamlit as st
import mimetypes
import os
from itertools import cycle
from lib.utils import styling, make_zip

def main():
    styling()

    st.title("Output")

    if "user_id" in st.session_state:
        output_folder = "user_data/output_" + st.session_state["user_id"]
        if os.path.exists(output_folder):

            col1, col2 = st.columns(2)
            col1.button("Make Zip", disabled= len(os.listdir(output_folder))==0, on_click = make_zip, args = (output_folder, col2))

            mimetypes.init()
            images=[]
            videos=[]
            for filename in os.listdir(output_folder):
                mimestart = mimetypes.guess_type(filename)[0]
                if mimestart != None:
                    mimestart = mimestart.split('/')[0]
                    if mimestart in ['image']:
                        images.append(os.path.join(output_folder, filename))
                    if mimestart in ['video']:
                        videos.append(os.path.join(output_folder, filename))
            cols = cycle(st.columns(3))
            for idx, image in enumerate(images):
                next(cols).image(image)
            for idx, video in enumerate(videos):
                next(cols).video(video)


if __name__ == '__main__':
    main()