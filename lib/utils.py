import streamlit as st
import datetime as dt
import subprocess
from icons import *
from lib.state import rendering

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

def execute(command, logfile):
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

def sidebar():
  if rendering :
      st.sidebar.success("Rendering...")

def update_state(var):
  path = "lib/state.py"
  file = open(path, "w") 
  file.write(var)
  file.close()