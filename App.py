import streamlit as st
import os
import socketserver

os.environ["CUDA_VISIBLE_DEVICES"] = "0,1"

from lib.utils import render_settings, performance, file_manager, execute
from lib.output import output

def main():

    with socketserver.TCPServer(("localhost", 0), None) as s:
        free_port = s.server_address[1]

    st.title("Blender Render Engine")
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🔥Render", "🎞️ Output", "📈 Performance", "📁 File Manager", "🐞 Debug"])
    with tab1:
        render_settings()
    with tab2:
        output()
    with tab3:
        performance()
    with tab4:
        file_manager(free_port)
    with tab5:
        # execute(f'browsepy 0.0.0.0 {free_port}')
        pass
        
if __name__ == '__main__':
    main()