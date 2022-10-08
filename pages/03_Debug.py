import streamlit as st
from streamlit_autorefresh import st_autorefresh
import os
from lib.utils import styling, sidebar

def main():
    styling()
    sidebar()
    st_autorefresh(interval=2000)

    st.title("Debug")

    logfile_path = "logs/render.log"
    if os.path.exists(logfile_path):
        file = open(logfile_path,mode='r')
        for line in file:
            if line.strip() != '' :
                st.write(f"`{line}`")
        file.close()

if __name__ == '__main__':
    main()