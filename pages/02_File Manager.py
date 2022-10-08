import streamlit as st
from lib.utils import styling, sidebar
import os, shutil

# list filse in dict format
# def tree(dir, folder):
#     for filename in os.listdir(dir):
#         if os.path.isdir(os.path.join(dir,filename)):
#             folder[filename] ={}
#             tree(os.path.join(dir,filename), folder[filename])
#         else:
#             folder[filename] = "file"
#     return folder

def  go_back():
    cur_path = st.session_state["current_path"]
    cur_path_idx = cur_path.rindex("/")
    st.session_state["current_path"] = st.session_state["current_path"][:cur_path_idx]

def next(next_path):
    st.session_state["current_path"] += "/"+next_path

def delete(path):
    del_path = st.session_state["current_path"]+"/"+path
    if os.path.exists(del_path):
        if os.path.isdir(del_path):
            shutil.rmtree(del_path)
        else:
            os.remove(del_path)

def list_files():
    path = st.session_state["current_path"]
    for i in os.listdir(path):
        full_path = f"{path}/{i}"
        if os.path.isdir(full_path):
            st.write("📁 "+i)
        else:
            st.write("🗃️ "+i)

def main():
    styling()
    sidebar()

    st.title("File Manager")

    st.write(os.path.dirname("./"))
    
    if "original_path" not in st.session_state :
        st.session_state["original_path"] = os.path.expanduser('~')
        st.session_state["current_path"] = st.session_state["original_path"]

    path = st.session_state["current_path"]
    og_path = st.session_state["original_path"]

    if os.path.exists(path):
        st.button("Go Back", disabled = path == og_path, on_click = go_back)
        del_path = st.selectbox("Delete", os.listdir(path))
        st.button("🗑️", disabled= len(os.listdir(path))==0, on_click = delete, args = [del_path])
        next_path = st.selectbox("Traverse", [name for name in os.listdir(path) if os.path.isdir(os.path.join(path, name))])
        st.button("Next", disabled = len([entry for entry in os.listdir(path) if os.path.isdir(os.path.join(path, entry))]) == 0, on_click = next, args = [next_path])
        st.markdown("***")
        list_files()

if __name__ == '__main__':
    main()