import streamlit as st
from lib.utils import styling
import os

def tree(dir, folder):
    for filename in os.listdir(dir):
        if os.path.isdir(os.path.join(dir,filename)):
            folder[filename] ={}
            tree(os.path.join(dir,filename), folder[filename])
        else:
            folder[filename] = "file"
    return folder

def main():
    styling()

    st.title("File Manager")

    if "browsepy_port" in st.session_state:
        browsepy_port = st.session_state["browsepy_port"]
        link=f'http://172.20.130.6:{browsepy_port}'
        st.caption(f"Serving on : {link}")
        html_string = f'<iframe style="border:2px solid #f63366; border-radius:10px;" width="600" height="400" src={link}></iframe>'
        st.markdown(html_string, unsafe_allow_html=True)

    else:
        st.write(tree(".",dict()))

if __name__ == '__main__':
    main()