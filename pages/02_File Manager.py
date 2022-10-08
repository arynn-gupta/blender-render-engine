import streamlit as st
from lib.utils import styling, sidebar
from pathlib import Path
import os, shutil
import psutil

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

def clear_download(output_file_name, col3):
    if os.path.exists(output_file_name):
        os.remove(output_file_name)
    col3.empty()

def download(download_file_path, col3):
    file_path = st.session_state["current_path"]+"/"+download_file_path
    file_name = Path(file_path).stem
    output_file_name = file_name + ".zip"
    if(os.path.isfile(file_path)):
        shutil.make_archive(file_name, 'zip', st.session_state["current_path"], download_file_path)
    else:
        shutil.make_archive(file_name, 'zip', file_path)
    file = open(f"{output_file_name}", "rb")
    col3.download_button(
            label="Download Zip",
            data=file,
            file_name=f"{output_file_name}",
            mime="application/zip",
            onclick=clear_download,
            args=(output_file_name, col3)
        )
    file.close()

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
    
    st.write(psutil.disk_partitions())

    if "original_path" not in st.session_state :
        st.session_state["original_path"] = "."
        st.session_state["current_path"] = st.session_state["original_path"]

    path = st.session_state["current_path"]
    og_path = st.session_state["original_path"]

    if os.path.exists(path):

        st.button("Go Back", disabled = path == og_path, on_click = go_back)

        next_path = st.selectbox("Traverse", [name for name in os.listdir(path) if os.path.isdir(os.path.join(path, name))])
        st.button("Next", disabled = len([entry for entry in os.listdir(path) if os.path.isdir(os.path.join(path, entry))]) == 0, on_click = next, args = [next_path])

        file_path = st.selectbox("File", os.listdir(path))
        col1, col2, col3 = st.columns(3)
        col1.button("🗑️", disabled= len(os.listdir(path))==0, on_click = delete, args = [file_path])
        col2.button("Make Zip", disabled= len(os.listdir(path))==0, on_click = download, args = (file_path, col3))

        st.markdown("***")
        list_files()

if __name__ == '__main__':
    main()