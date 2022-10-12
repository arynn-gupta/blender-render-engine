import streamlit as st
import wget
import os, subprocess, shutil, zipfile, tarfile, random, string
import datetime as dt
import mimetypes

os.environ["CUDA_VISIBLE_DEVICES"] = "0,1"

from lib.utils import styling

banner = '''
   ___              __        _  __
  / _ \___ ___  ___/ /__ ____| |/_/
 / , _/ -_) _ \/ _  / -_) __/>  <  
/_/|_|\__/_//_/\_,_/\__/_/ /_/|_|  v1.0
'''

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

@st.cache
def generate_random_id():
  return ''.join(random.choices(string.ascii_letters + string.digits, k=16))

def main():
    styling()
    
    st.title("Blender Render Engine")

    if "user_id" not in st.session_state :
        st.session_state["user_id"] = generate_random_id()

    user_id = st.session_state["user_id"]
    
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
        end_frame = start_frame

    output_name = st.text_input("Output Name", value="blender-####")

    gpu_enabled = st.checkbox("GPU Render", value=True)
    cpu_enabled = st.checkbox("CPU Render", value=True)
    continuous_render = st.checkbox("Render Without Output", value=False)
    if continuous_render:
        st.info("This will increase render speed but you won't be able to see any output !")

    submit = st.button("Start Render")

    if submit and uploaded_file is not None :

        if animation :
            if start_frame == end_frame or start_frame>end_frame :
                info.error("Please enter a valid start and end frame !")
                st.stop()

        log_file = "logs/log_" + user_id + ".log"
        project_folder = "user_data/project_" + user_id
        output_folder = "user_data/output_" + user_id
        output_path = output_folder + '/' + output_name
        setup_file = "user_data/setgpu_" + user_id + ".py"
        renderer = "CUDA"
        info = st.empty()
        script = []
        output_images = []
        mimetypes.init()

        if os.path.isdir(project_folder):
            shutil.rmtree(project_folder)
        os.makedirs(project_folder)

        if os.path.isdir(output_folder):
            shutil.rmtree(output_folder)
        os.makedirs(output_folder)

        if os.path.isfile(setup_file):
            os.remove(setup_file)

        if not os.path.isdir("logs"):
            os.mkdir("logs")
        
        if (uploaded_file.name.split('.')[-1] == 'zip'):
            blend_file_path = project_folder + "/" + blend_file_path
            info.success("Extracting Project...")
            with zipfile.ZipFile(uploaded_file, 'r') as zip_ref:
                zip_ref.extractall(project_folder)
            if not os.path.exists(blend_file_path):
                info.error("Couldn't find blend file inside project please provide a valid Blend File Path !")
                st.stop()
        else:
            blend_file_path = project_folder + "/" + uploaded_file.name
            file = open(blend_file_path, 'wb')
            file.write(uploaded_file.getvalue())
            file.close()

        file = open(log_file, "a") 
        file.write("\n")
        file.write("-"*21)
        file.write("Generated on : "+str(dt.datetime.now())+"\n")
        file.write(banner)
        file.write("-"*21)
        file.write("\n")
        file.close()

        info.success("Installing Blender...")

        blender_url = blender_url_dict[blender_version]
        base_url = os.path.basename(blender_url)
        if (not os.path.isdir(blender_version)):
            wget.download(blender_url)
            file = tarfile.open(base_url)
            file.extractall("./")
            file.close()
            os.rename(f"{base_url.replace('.tar.xz', '')}", f"{blender_version}")

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
        file = open(setup_file, 'w')
        file.write(data)
        file.close()

        if animation:
            if continuous_render:
                script.append(f'''
                ./{blender_version}/blender -b '{blend_file_path}' -P setgpu.py -E CYCLES -o '{output_path}' -noaudio -s {start_frame} -e {end_frame} -a -- --cycles-device "{renderer}"
                ''')
            else :
                for i in range(start_frame, end_frame+1):
                    script.append(f'''
                        ./{blender_version}/blender -b '{blend_file_path}' -P setgpu.py -E CYCLES -o '{output_path}' -noaudio -f {i} -- --cycles-device "{renderer}"
                        ''')
        else:
            script.append(f'''
                ./{blender_version}/blender -b '{blend_file_path}' -P setgpu.py -E CYCLES -o '{output_path}' -noaudio -f {start_frame} -- --cycles-device "{renderer}"
                ''')

        info.success("Rendering...")

        for i in script:

            output = subprocess.check_output(script, shell=True)
            file = open(log_file, "a") 
            file.write(output.decode("utf-8") +"\n")
            file.close()

            if not continuous_render :
                for i in os.listdir(output_folder):
                    if i not in output_images:
                        mimestart = mimetypes.guess_type(i)[0]
                        if mimestart != None:
                            mimestart = mimestart.split('/')[0]
                            if mimestart in ['image']:
                                st.image(os.path.join(output_folder, i))
                            if mimestart in ['video']:
                                st.video(os.path.join(output_folder, i))
                        output_images.append(i)
            
        info.success("Finished !")
        shutil.rmtree(project_folder)
        os.remove(setup_file)
        
if __name__ == '__main__':
    main()