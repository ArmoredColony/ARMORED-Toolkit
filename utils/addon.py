import bpy
import os

# DO NOT IMPORT OTHER ADDON MODULES HERE. YOU RISK CIRCULAR IMPORT ERRORS.


def path():
    return os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

def name():
    return __package__.split(".")[0]

def addon():
    return bpy.context.preferences.addons[name()]

def prefs():
    return addon().preferences

def debug():
    return prefs().debug