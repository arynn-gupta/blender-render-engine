import streamlit as st
from lib.utils import styling, logs

def main():
    styling()

    st.title("Debug")
    
    logs("browsepy")
    logs("blender")
    logs("render")

if __name__ == '__main__':
    main()