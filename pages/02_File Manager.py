import streamlit as st
from lib.utils import styling, sidebar, make_zip
import os, shutil

# list files in dict format
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

def next(next_path, ele):
    path = st.session_state["current_path"] + "/"+next_path
    if os.path.isdir(path):
        st.session_state["current_path"] = path
    else:
        ele[0].error("It's a file 🥲")

def delete(path):
    del_path = st.session_state["current_path"]+"/"+path
    if os.path.exists(del_path):
        if os.path.isdir(del_path):
            shutil.rmtree(del_path)
        else:
            os.remove(del_path)

def list_files():
    path = st.session_state["current_path"]
    for i in sorted(os.listdir(path), key=sort_by_type):
        full_path = f"{path}/{i}"
        if os.path.isdir(full_path):
            st.write("📁 "+i)
        else:
            st.write("🗃️ "+i)

def sort_by_type(x):
    return os.path.splitext(x)[::-1]

def view_file(path, ele):
    if os.path.isfile(path):
        file = open(path,mode='r')
        for line in file:
            ele[0].write(line)
        file.close()
    else:
        ele[0].error("It's a folder 🥲")

def main():
    styling()
    sidebar()

    st.title("File Manager")

    if "original_path" not in st.session_state :
        st.session_state["original_path"] = "."
        st.session_state["current_path"] = st.session_state["original_path"]

    path = st.session_state["current_path"]
    og_path = st.session_state["original_path"]

    if os.path.exists(path):

        st.button("Go Back", disabled = path == og_path, on_click = go_back)

        file_path = st.selectbox("", sorted(os.listdir(path), key=sort_by_type))
        col1, col2, col3, col4, col5 = st.columns(5)
        row = st.columns(1)
        col1.button("Traverse", disabled = len([entry for entry in os.listdir(path) if os.path.isdir(os.path.join(path, entry))]) == 0, on_click = next, args = (file_path, row))
        col2.button("View File", disabled= len(os.listdir(path))==0, on_click = view_file, args = (file_path, row))
        col3.button("Make Zip", disabled= len(os.listdir(path))==0, on_click = make_zip, args = (file_path, col4))
        col5.button("🗑️", disabled= len(os.listdir(path))==0, on_click = delete, args = [file_path])

        st.markdown("***")
        st.write("")
        list_files()

if __name__ == '__main__':
    main()