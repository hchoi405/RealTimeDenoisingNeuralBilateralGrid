import os
import numpy as np
import exr
import parmap
from functools import partial
from skimage.metrics import structural_similarity
import glob

scenes = [
    ("data_Arcade", 103),
    ("data_BistroExterior", 103),
    ("data_BistroExterior2", 103),
    ("data_Classroom", 603),
    ("data_Dining-room", 103),
    ("data_Dining-room-dynamic", 140),
    ("data_Staircase", 450)
]

def mse_loss(img1, img2):
    return np.mean((img1 - img2) ** 2)

def relmse_loss(y_true, y_pred):
    y_pred = np.clip(y_pred, 0, None)
    true_mean = np.mean(y_true, axis=2, keepdims=True)
    return np.average(np.square(y_pred - y_true) / (np.square(true_mean) + 1e-2))

# Definition from ANF
def smape_loss(y_true, y_pred):
    numerator = np.abs(y_true - y_pred).sum(axis=2, keepdims=True)
    denominator = np.abs(y_true).sum(axis=2, keepdims=True) + \
        np.abs(y_pred).sum(axis=2, keepdims=True)
    return np.mean(numerator / (denominator + 1e-2)) / 3

def tone_mapping(y):
    y = np.clip(y, 0, None)  # non-negative
    y = np.power(y / (y + 1), 1 / 2.2)  # gamma correction
    return y

def psnr_loss(y_true, y_pred):
    # HDR -> LDR
    y_true = tone_mapping(y_true)
    y_pred = tone_mapping(y_pred)

    mse = np.mean((y_true - y_pred) ** 2)
    return -10 * np.log10(mse)

# higher is better
def ssim_loss(y_true, y_pred):
    # HDR -> LDR
    y_true = tone_mapping(y_true)
    y_pred = tone_mapping(y_pred)

    val = structural_similarity(y_true, y_pred, multichannel=True, data_range=y_pred.max() - y_pred.min())
    return val

img_cache = {}
def load_frame(scene, model, loss_fn, i):
    ref_path = f'/dataset_falcor/{scene}/ref_modul_{i:04d}.exr'
    pred_path = f'/nas/nbg/{scene}/{model}/nbg_{i:04d}.exr'
    if ref_path not in img_cache:
        img_cache[ref_path] = exr.read_all(ref_path)['default']
    if pred_path not in img_cache:
        img_cache[pred_path] = exr.read_all(pred_path)['default']
    img_ref = img_cache[ref_path]
    img_pred = img_cache[pred_path]
    return loss_fn(img_ref, img_pred)

def compare_models(loss_fn):
    scene_errors = {}
    for scene, scene_frames in scenes:
        scene_errors[scene] = {}
        model_errors = []
        for model_path in glob.glob(f'/nas/nbg/{scene}/*/'):
            model = os.path.basename(os.path.normpath(model_path))
            frames = range(scene_frames)
            # Check if losses have already been calculated in losses folder as a text file
            loss_filename = f'losses/{scene}_{model}_{loss_fn.__name__}.txt'
            regenerate = False
            if os.path.exists(loss_filename):
                with open(loss_filename, 'r') as f:
                    errors = [float(x) for x in f.read().splitlines()]
                # Check if the number of errors is correct
                if len(errors) != scene_frames:
                    print(f'Number of errors in {loss_filename} is not correct.')
                    regenerate = True
            else:
                regenerate = True
            
            if regenerate:
                print(f'Regenerating losses... {scene} {model} {loss_fn.__name__}')
                load_fn = partial(load_frame, scene, model, loss_fn)
                errors = parmap.map(load_fn, frames, pm_processes=20)
                # Save losses to text file
                with open(loss_filename, 'w') as f:
                    for error in errors:
                        f.write(f'{error}\n')
            model_errors.append(errors)

        model_errors = np.array(model_errors)
        avg_error = np.mean(model_errors, axis=1)
        if loss_fn == ssim_loss or loss_fn == psnr_loss:
            best_model_idx = np.argmax(avg_error)
        else:
            best_model_idx = np.argmin(avg_error)
        best_model = os.path.basename(os.path.normpath(glob.glob(f'/nas/nbg/{scene}/*/')[best_model_idx]))
        scene_errors[scene]['avg'] = avg_error
        scene_errors[scene]['best_model'] = best_model
        scene_errors[scene]['best_error'] = avg_error[best_model_idx]
    return scene_errors

if __name__ == '__main__':
    for loss_fn in [mse_loss, relmse_loss, smape_loss, psnr_loss, ssim_loss]:
        scene_errors = compare_models(loss_fn)
        print(f'{loss_fn.__name__}:')
        for scene in scene_errors:
            avg_error = np.mean(scene_errors[scene]['avg'])
            min_error = np.min(scene_errors[scene]['avg'])
            max_error = np.max(scene_errors[scene]['avg'])
            std_error = np.std(scene_errors[scene]['avg'])
            best_model = scene_errors[scene]['best_model']
            best_error = scene_errors[scene]['best_error']
            print(f'Scene {scene}:')
            print(f'\tBest model: {best_model}')
            print(f'\tBest error: {best_error:.6f}')
            print(f'\tavg error: {avg_error:.6f}')
            print(f'\tmin error: {min_error:.6f}')
            print(f'\tmax error: {max_error:.6f}')
            print(f'\tstd error: {std_error:.6f}')
        print()
    print('End.')
