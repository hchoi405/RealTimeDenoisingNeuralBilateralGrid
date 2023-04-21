import os
import shutil
import subprocess

models = ['classroom', 'living-room', 'san-miguel', 'sponza', 'sponza-glossy', 'sponza-moving-light']
scenes = [
    # ("data_Arcade", 103), 
    # ("data_BistroExterior", 103), 
    # ("data_BistroExterior2", 103), 
    # ("data_Classroom", 603), 
    # ("data_Dining-room", 103), 
    # ("data_Dining-room-dynamic", 140), 
    ("data_Staircase", 450)
]

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

start = False
# Iterate scenes
for scene, num_frames in scenes:
    # Iterate models moving files to output folder
    for model in models:
        # Skip until (model == classroom and scene == data_Dining-room-dynamic)
        if scene == 'data_Staircase' and model == 'san-miguel':
            start = True
        if not start:
            continue

        os.makedirs(f'output/{scene}/{model}', exist_ok=True)

        print(f"Processing scene: {scene}, total frame: {num_frames}, model: {model}")
        for i in range(num_frames):
            print(f'\tframe: {i}')
            
            command = f"python network_test.py -m {model} -s test_Falcor -r /dataset_falcor -d {scene} -ts {num_frames} -t {i} --export_exr"
            try:
                subprocess.check_call(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
            except subprocess.CalledProcessError as e:
                print(f"Error: {e.output.decode()}")

            os.makedirs(f"output/{scene}", exist_ok=True)
            for file in os.listdir(f"results/{scene}/result/test_out"):
                src = f'results/{scene}/result/test_out/{file}'
                dst = f'output/{scene}/{model}/{file}'
                os.rename(src, dst)

        # rename_directory(os.path.join("output", scene), os.path.join("output", f'{model}_{scene}'))

        # Make sure the directory exists in the NAS
        os.makedirs(f"/nas/nbg/{scene}/{model}", exist_ok=True)

        # # Move all files through rsync and remove original files in asynchronous process
        subprocess.Popen(["rsync", "-av", "--no-o", "--no-g", "--remove-source-files", 
            f"output/{scene}/{model}/",
            f"/nas/nbg/{scene}/{model}/"
            ])
