import os
import shutil

from . import debug


def make_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)
    return path


def copy_files(source_path, target_path):
    target_path = make_dir(target_path)

    for file in os.listdir(source_path):
        if file not in os.listdir(target_path):
            shutil.copy(os.path.join(source_path, file), target_path)
            debug.msg(f'Added {file}')

def delete_files(file_names: list, target_path):
    if not os.path.exists(target_path):
        return

    for file in file_names:
        if file in os.listdir(target_path):
            os.remove(os.path.join(target_path, file))
            debug.msg(f'Removed {file}')