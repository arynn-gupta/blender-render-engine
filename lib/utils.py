import streamlit as st
import platform
import psutil
from gpuinfo.nvidia import get_gpus
from cpuinfo import get_cpu_info
import math
import mimetypes
import shutil
import zipfile
import wget
import subprocess
from itertools import cycle
import os

blender_url_dict = {
    '2.79b'   : "https://ftp.nluug.nl/pub/graphics/blender/release/Blender2.79/blender-2.79b-linux-glibc219-x86_64.tar.bz2",
    '2.80rc3' : "https://ftp.nluug.nl/pub/graphics/blender/release/Blender2.80/blender-2.80rc3-linux-glibc217-x86_64.tar.bz2",
    '2.81a'   : "https://ftp.nluug.nl/pub/graphics/blender/release/Blender2.81/blender-2.81a-linux-glibc217-x86_64.tar.bz2",
    '2.82a'   : "https://ftp.nluug.nl/pub/graphics/blender/release/Blender2.82/blender-2.82a-linux64.tar.xz",
    '2.83.20' : "https://ftp.nluug.nl/pub/graphics/blender/release/Blender2.83/blender-2.83.20-linux-x64.tar.xz",
    '2.90.1'  : "https://ftp.nluug.nl/pub/graphics/blender/release/Blender2.90/blender-2.90.1-linux64.tar.xz",
    '2.91.2'  : "https://ftp.nluug.nl/pub/graphics/blender/release/Blender2.91/blender-2.91.2-linux64.tar.xz",
    '2.92.0'  : "https://ftp.nluug.nl/pub/graphics/blender/release/Blender2.92/blender-2.92.0-linux64.tar.xz",
    '2.93.10' : "https://ftp.nluug.nl/pub/graphics/blender/release/Blender2.93/blender-2.93.10-linux-x64.tar.xz",
    '3.0.1'   : "https://ftp.nluug.nl/pub/graphics/blender/release/Blender3.0/blender-3.0.1-linux-x64.tar.xz",
    '3.1.2'   : "https://ftp.nluug.nl/pub/graphics/blender/release/Blender3.1/blender-3.1.2-linux-x64.tar.xz",
    '3.2.2'   : "https://ftp.nluug.nl/pub/graphics/blender/release/Blender3.2/blender-3.2.2-linux-x64.tar.xz",
    '3.3.0'   : "https://ftp.nluug.nl/pub/graphics/blender/release/Blender3.3/blender-3.3.0-linux-x64.tar.xz"
}

# subscribe to subprocess output
@st.cache(suppress_st_warning=True)
def execute(command):
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    output = ''
    
    for line in iter(process.stdout.readline, ""):
        try:
            line = line.decode("utf-8") 
            if (line != ''):
                st.markdown(f"`{line}`")
        except:
            pass

    process.wait()
    exitCode = process.returncode

    if (exitCode == 0):
        return output
    else:
        raise Exception(command, exitCode, output)

# Dictionary of whole directory tree 
def tree(dir, folder):
    for filename in os.listdir(dir):
        if os.path.isdir(os.path.join(dir,filename)):
            folder[filename] ={}
            tree(os.path.join(dir,filename), folder[filename])
        else:
            folder[filename] = "file"
    return folder

def convert_size(size_bytes):
   if size_bytes == 0:
       return "0B"
   size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
   i = int(math.floor(math.log(size_bytes, 1024)))
   p = math.pow(1024, i)
   s = round(size_bytes / p, 2)
   return "%s %s" % (s, size_name[i])

def performance():
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

    st.write(tree(".",dict()))

def file_manager(port):
    link=f"http://172.20.130.6:{port}"
    st.caption(f"Serving on : {link}")
    html_string = f'<iframe style="border:2px solid #f63366; border-radius:10px;" width="600" height="400" src={link}></iframe>'
    st.markdown(html_string, unsafe_allow_html=True)

def start_render():
    st.session_state['rendering'] = True
    if "output" in st.session_state:
        del st.session_state['output']

def finish_render(output_file_name):
    st.session_state["output"] = output_file_name
    if "rendering" in st.session_state:
        del st.session_state['rendering']

def render_settings():
    uploaded_file = st.file_uploader("", type=['blend', 'zip'])
    blender_version = st.selectbox("Blender Version", ['2.79b', '2.80rc3', '2.81a', '2.82a', '2.83.20', '2.90.1', '2.91.2', '2.92.0', '2.93.10', '3.0.1', '3.1.2', '3.2.2', '3.3.0'][::-1])
    if( uploaded_file is not None ):
        if (uploaded_file.name.split('.')[-1] == 'zip') : blend_file_path=st.text_input("Blend File Path")
        else : blend_file_path = uploaded_file.name
        
    render_type = st.selectbox('Render Type', ["Image", "Animation"])
    if render_type == "Animation":
        animation = True
        start_frame = st.number_input("Start Frame", min_value=0 , step=1)
        end_frame = st.number_input("End Frame", min_value=0 , step=1)
    else:
        animation = False
        start_frame = st.number_input("Frame", min_value=0 , step=1)

    gpu_enabled = st.checkbox("GPU Render", value=True)
    cpu_enabled = st.checkbox("CPU Render", value=True)

    output_name = st.text_input("Output Name", value="blender-####")

    btn = st.empty()
    submitted = btn.button("Start Render", key="submitted", on_click=start_render)

    if submitted and uploaded_file is not None :
        submitted = btn.button("Rendering", disabled=True, key="submitted_disabled")

        if (os.path.isdir("project")):
            shutil.rmtree("project")
        os.mkdir("project")
        if (os.path.isdir("output")):
            shutil.rmtree("output")
        os.mkdir("output")

        if (uploaded_file.name.split('.')[-1] == 'zip'):
            with zipfile.ZipFile(uploaded_file, 'r') as zip_ref:
                zip_ref.extractall("project")
        else:
            with open(f"project/{uploaded_file.name}", 'wb') as f: 
                f.write(uploaded_file.getvalue())

        blender_url = blender_url_dict[blender_version]
        base_url = os.path.basename(blender_url)
        if (not os.path.isdir(blender_version)):
            os.mkdir(blender_version)
            wget.download(blender_url)
            subprocess.run(["tar", "-xkf", base_url, "-C", "./"+blender_version, "--strip-components=1"], check=True)

        # Enable GPU rendering (or add custom properties here)
        if not gpu_enabled and not cpu_enabled:
            cpu_enabled=True
        data = "import re\n"+\
            "import bpy\n"+\
            "scene = bpy.context.scene\n"+\
            "scene.cycles.device = 'GPU'\n"+\
            "prefs = bpy.context.preferences\n"+\
            "prefs.addons['cycles'].preferences.get_devices()\n"+\
            "cprefs = prefs.addons['cycles'].preferences\n"+\
            "print(cprefs)\n"+\
            "for compute_device_type in ('CUDA', 'OPENCL', 'NONE'):\n"+\
            "    try:\n"+\
            "        cprefs.compute_device_type = compute_device_type\n"+\
            "        print('Device found:',compute_device_type)\n"+\
            "        break\n"+\
            "    except TypeError:\n"+\
            "        pass\n"+\
            "for device in cprefs.devices:\n"+\
            "    if not re.match('intel', device.name, re.I):\n"+\
            "        print('Activating',device)\n"+\
            "        device.use = "+str(gpu_enabled)+"\n"+\
            "    else:\n"+\
            "        device.use = "+str(cpu_enabled)+"\n"
        with open('setgpu.py', 'w') as f:
            f.write(data)
        renderer = "CUDA"

        output_path = 'output/' + output_name

        if animation:
            if start_frame == end_frame:
                script=f'''
                ./{blender_version}/blender -b 'project/{blend_file_path}' -P setgpu.py -E CYCLES -o '{output_path}' -noaudio -a -- --cycles-device "{renderer}"
                '''
            else:
                script=f'''
                ./{blender_version}/blender -b 'project/{blend_file_path}' -P setgpu.py -E CYCLES -o '{output_path}' -noaudio -s {start_frame} -e {end_frame} -a -- --cycles-device "{renderer}"
                '''
        else:
            script=f'''
                ./{blender_version}/blender -b 'project/{blend_file_path}' -P setgpu.py -E CYCLES -o '{output_path}' -noaudio -f {start_frame} -- --cycles-device "{renderer}"
                '''
        subprocess.run(script, shell=True)

        output_file_name = output_name.replace('#', '') + 'render'
        shutil.make_archive(output_file_name, 'zip', 'output')
        
        finish_render(output_file_name)
        submitted = btn.button("Start Render", key="submitted2", on_click=start_render)

def render_output():
    if "rendering" in st.session_state :
        st.success("Rendering...")
    elif "output" in st.session_state :
        output_folder_name = st.session_state["output"]
        with open(f"{output_folder_name}.zip", "rb") as file:
            st.download_button(
                    label="Download Zip",
                    data=file,
                    file_name=f"{output_folder_name}.zip",
                    mime="application/zip"
                )

    mimetypes.init()
    images=[]
    videos=[]
    if (os.path.isdir("output")):
        for filename in os.listdir("output"):
            mimestart = mimetypes.guess_type(filename)[0]
            if mimestart != None:
                mimestart = mimestart.split('/')[0]
                if mimestart in ['image']:
                    images.append(os.path.join("output", filename))
                if mimestart in ['video']:
                    videos.append(os.path.join("output", filename))
        cols = cycle(st.columns(3))
        for idx, image in enumerate(images):
            next(cols).image(image)
        for idx, video in enumerate(videos):
            next(cols).video(video)
