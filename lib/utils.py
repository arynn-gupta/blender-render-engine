import streamlit as st
import datetime as dt
import os, subprocess, shutil
from icons import *
from lib.state import rendering
from pathlib import Path

style='''
div.css-1gk2i2l.e17lx80j0 {
  width: 100%;
  height: 250px;
  display: flex;
  align-items: center;
  justify-content: center;
}

h1 span {
  color: #893aff;
}

h3 span {
  color: #06b48b;
}

li path {
  display: none;
}

li {
  padding: none;
}

li span {
  width: 100%;
  margin-right: 1.2rem;
  margin-bottom: 0.5rem;
  padding: 0.5rem 2rem;
  color: #b4b6be;
  border-radius: 0.5rem;
}

li span:before{
    margin-right: 8px; position: relative;  top: 2px; 
}

li span:hover {
  color: white;
  background-color: #313334;
}

a {
  background: none !important;
}

a.css-1m59598.e1fqkh3o6 span{
  color: white;
  background-color: #313334;
}
'''

def styling():
  st.markdown(f"<style>{style}</style>", unsafe_allow_html=True)
  st.markdown('''<style>
      li:nth-child(1) span:before {  content: '''+fire+'''; }
      li:nth-child(2) span:before {  content: '''+film+'''; }
      li:nth-child(3) span:before {  content: '''+cpu+'''; }
      li:nth-child(4) span:before {  content: '''+folder+'''; }
      li:nth-child(5) span:before {  content: '''+bug+'''; }
  </style>''', unsafe_allow_html=True)

def background_render(command, logfile):
  file = open("logs/"+logfile+".log", "a") 
  file.write(str(dt.datetime.now())+"\n")
  file.flush()
  process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

  for line in iter(process.stdout.readline, ""):
    try:
      line = line.decode("utf-8") 
      if (line != ''):
          file.write(line)
          file.flush()
    except:
      pass
  file.close()

  return_code = process.wait()
  if return_code:
    raise subprocess.CalledProcessError(return_code, command)
  else:
    update_state("rendering = False")

def sidebar():
  if rendering :
      st.sidebar.success("Rendering...")

def update_state(var):
  path = "lib/state.py"
  file = open(path, "w") 
  file.write(var)
  file.close()


def clear_download(output_file_name, ele):
    if os.path.exists(output_file_name):
        os.remove(output_file_name)
    ele.empty()

def make_zip(download_file_path, ele):
    file_path = st.session_state["current_path"]+"/"+download_file_path
    file_name = Path(file_path).stem
    output_file_name = file_name + ".zip"
    if(os.path.isfile(file_path)):
        shutil.make_archive(file_name, 'zip', st.session_state["current_path"], download_file_path)
    else:
        shutil.make_archive(file_name, 'zip', file_path)
    file = open(f"{output_file_name}", "rb")
    ele.download_button(
            label="Download Zip",
            data=file,
            file_name=f"{output_file_name}",
            mime="application/zip",
            on_click =clear_download,
            args=(output_file_name, ele)
        )
    file.close()