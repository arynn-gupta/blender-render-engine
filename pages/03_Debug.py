import streamlit as st
from lib.utils import styling, sidebar
import os, subprocess, select

def main():
    styling()
    sidebar()

    st.title("Debug")

    logfile_path = "logs/render.log"
    if "tailing" not in st.session_state  and os.path.exists(logfile_path):
        st.session_state["tailing"] = True
        f = subprocess.Popen(['tail','-F', logfile_path], stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        p = select.poll()
        p.register(f.stdout)

        while True:
            if p.poll(1):
                st.write(f.stdout.readline())

if __name__ == '__main__':
    main()