import streamlit as st
import os
from lib.utils import styling

def main():
    styling()

    st.title("Debug")

    if "user_id" in st.session_state:
        logfile_path = "logs/log_" + st.session_state["user_id"] + ".log"
        if os.path.exists(logfile_path):
            file = open(logfile_path,mode='r')
            for line in file:
                if line.strip() != '' :
                    st.write(f"`{line}`")
            file.close()

if __name__ == '__main__':
    main()