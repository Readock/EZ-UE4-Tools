import subprocess
import os
import bpy
from . import addon

def is_perforce_installed():
    '''check if p4 command line tool is installed'''
    try:
        subprocess.call(["p4", "info"])
    except Exception as e:
        return False
    return True

def checkout_blend_file():
    '''performe checkout'''
    filepath = addon.get_blend_file_path()
    subprocess.run(["p4", "edit", filepath])

def is_blend_file_checked_out():
    '''Is the file currently saved and checked out'''
    if not addon.is_blend_file_saved():
        return False
    filepath = addon.get_blend_file_path()
    return os.access(filepath, os.W_OK)

def is_checkout_needed():
    '''Is a checkout before saving needed'''
    if not addon.is_blend_file_saved():
        return False
    return not is_blend_file_checked_out()