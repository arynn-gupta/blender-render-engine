import streamlit as st
import math, platform
import psutil
from gpuinfo.nvidia import get_gpus
from cpuinfo import get_cpu_info
from lib.utils import styling, sidebar

def convert_size(size_bytes):
   if size_bytes == 0:
       return "0B"
   size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
   i = int(math.floor(math.log(size_bytes, 1024)))
   p = math.pow(1024, i)
   s = round(size_bytes / p, 2)
   return "%s %s" % (s, size_name[i])

def main():
    styling()
    sidebar()

    st.title("Performance")

    info = get_cpu_info()
    ram = convert_size(psutil.virtual_memory().total)
    ram_used = convert_size(psutil.virtual_memory().used)
    ram_available = convert_size(psutil.virtual_memory().available)
    storage = convert_size(psutil.disk_usage('/').total)
    storage_used = convert_size(psutil.disk_usage('/').used)
    storage_available = convert_size(psutil.disk_usage('/').free)
    
    for gpu in get_gpus():
        gpu_name = (gpu.__dict__['name'])
        vram = round((gpu.__dict__['total_memory']) / 1024, 2)
        vram_used = round((gpu.get_memory_details()["used_memory"]) / 1024, 2)
        vram_available = round((gpu.get_memory_details()["free_memory"]) / 1024, 2)

    st.subheader("System Info")
    st.caption(f'''
    OS : {platform.platform()} \n
    CPU : {info['brand_raw']} \n
    RAM : {ram} , Used : {ram_used} , Available : {ram_available} \n
    GPU : {gpu_name} \n
    VRAM : {vram} GB , Used : {vram_used} GB , Available : {vram_available} GB \n
    Storage : {storage} , Used : {storage_used} , Available : {storage_available} \n
    Python : {info['python_version']} \n
    ''')

if __name__ == '__main__':
    main()