import os
import shutil
import subprocess

num_frames = 301

# Based on PSNR loss and ~103 frames

scenes = ["data_Classroom", "data_Dining-room", "data_Staircase"]
models = ["classroom"]

def rename_directory(old_name, new_name):
    # Rename the directory
    try:
        # Rename the directory
        os.rename(old_name, new_name)
    except OSError as e:
        # print(f'{new_name} already exists. Copying files from {old_name} to {new_name} and deleting {old_name}')
        # Check if the new directory name already exists
        if os.path.exists(new_name):
            # Copy all files from old directory to new directory
            for filename in os.listdir(old_name):
                src = os.path.join(old_name, filename)
                dst = os.path.join(new_name, filename)
                shutil.copy2(src, dst)

            # Delete the old directory
            shutil.rmtree(old_name)

# Iterate scenes
for scene in scenes:
    for model in models:
        dst_dir = f"output/{scene}_{model}"
        os.makedirs(dst_dir, exist_ok=True)

        print(f"Processing scene: {scene}, total frame: {num_frames}, model: {model}")
        for i in range(num_frames):
            if scene == "data_Classroom" and i < 180: continue
            print(f'\tframe: {i}')
            
            # command = f"python network_test.py -m classroom -s test -r ./dataset -d classroom -ts 60 -t 0"
            # command = f"python network_test.py -m sponza-moving-light -s test_Falcor -r ./dataset_falcor -d data_BistroExterior2 -ts 103 -t 0"
            command = f"python network_test.py -m {model} -s test_Falcor -r /dataset_falcor/dataset_new -d {scene} -ts {num_frames} -t {i} --export_exr"
            try:
                subprocess.check_call(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except subprocess.CalledProcessError as e:
                print(f"Error: {e.output.decode()}")

            for file in os.listdir(f"results/{scene}/result/test_out"):
                src = f'results/{scene}/result/test_out/{file}'
                dst = f'{dst_dir}/{file}'
                os.rename(src, dst)

        # # Make sure the directory exists in the NAS
        # os.makedirs(f"/nas/nbg/{scene}/", exist_ok=True)

        # # # Move all files through rsync and remove original files in asynchronous process
        # subprocess.Popen(["rsync", "-av", "--no-o", "--no-g", "--remove-source-files", 
        #     dst_dir,
        #     f"/nas/nbg/"
        #     ])
