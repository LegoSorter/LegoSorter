# python
import sys
from distutils.dir_util import copy_tree

# blender
import bpy
import addon_utils

argv = sys.argv
argv = argv[argv.index("--") + 1:]

addon_path = argv[0]
addons_dir = bpy.utils.script_path_user() + "/addons/importldraw"

copy_tree(addon_path, addons_dir)

addon_utils.enable("importldraw")
bpy.ops.wm.save_userpref()