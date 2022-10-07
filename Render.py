import streamlit as st
import wget
import os, shutil, zipfile

os.environ["CUDA_VISIBLE_DEVICES"] = "0,1"

from lib.utils import styling, execute, initialize

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

def main():
    styling()
    initialize()
    
    st.title("Blender Render Engine")
    
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
    submitted = btn.button("Start Render", key="submitted")

    if submitted and uploaded_file is not None :
        submitted = btn.button("Rendering", disabled=True, key="submitted_disabled")
        st.session_state['rendering'] = True

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
            execute(["tar", "-xkf", base_url, "-C", "./"+blender_version, "--strip-components=1"], logfile="blender")

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

        if os.path.exists(f'project/{blend_file_path}'):
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
            execute(script, logfile="render")
        else :
            st.error("Blend file path doesn't exist.")

        if "rendering" in st.session_state:
            del st.session_state['rendering']
        
if __name__ == '__main__':
    main()