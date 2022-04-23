import subprocess
import os
import bpy
from . import addon

def is_perforce_installed():
    try:
        subprocess.call(["p4", "info"])
    except Exception as e:
        return False
    return True

def checkout_blend_file():
    filepath = addon.get_blend_file_path()
    subprocess.run(["p4", "edit", filepath])

def is_blend_file_readable():
    if not addon.is_blend_file_saved():
        return False
    filepath = addon.get_blend_file_path()
    return os.access(filepath, os.W_OK)