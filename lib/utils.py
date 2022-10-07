import streamlit as st
import datetime as dt
import os, time, subprocess, socketserver, shutil
from icons import *

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

def subscribe_file(thefile):
  thefile.seek(0,2)
  while True:
      line = thefile.readline()
      if not line:
          time.sleep(0.1)
          continue
      yield line

def logs(logfile):
  logfile_path = "logs/"+logfile+".log"
  if os.path.exists(logfile_path):
      logfile = open(logfile_path,"r")
      loglines = subscribe_file(logfile)
      for line in loglines:
          st.write(f"`{line}`")

def execute(command, logfile):
  with open("logs/"+logfile+".log", "w") as file:
    file.write(dt.datetime.now()+"\n")
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    output = ''
    
    for line in iter(process.stdout.readline, ""):
        try:
            line = line.decode("utf-8") 
            if (line != ''):
              file.write(line+"\n")
        except:
            pass

    process.wait()
    exitCode = process.returncode

    if (exitCode == 0):
        return output
    else:
        raise Exception(command, exitCode, output)

def browsepy_server():
  with socketserver.TCPServer(("localhost", 0), None) as s:
      free_port = s.server_address[1]
  st.session_state["browsepy_port"] = free_port
  execute(f'browsepy 0.0.0.0 {free_port}', logfile="browsepy")

def initialize():
  if not "initialized" in st.session_state:
    st.session_state["initialized"] = True
    browsepy_server()
    if (not os.path.isdir("logs")):
        os.mkdir("logs")