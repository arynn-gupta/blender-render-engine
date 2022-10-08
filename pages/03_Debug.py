import streamlit as st
from lib.utils import styling, sidebar
from streamlit_autorefresh import st_autorefresh

def main():
    styling()
    sidebar()
    st_autorefresh(interval=5000)

    st.title("Debug")

    logfile_path = "logs/render.log"
    file = open(logfile_path,mode='r')
    file.read()
    file.close()

if __name__ == '__main__':
    main()