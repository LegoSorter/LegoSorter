# python
import sys
import os
from distutils.dir_util import copy_tree

# blender
import bpy
import addon_utils

argv = sys.argv
argv = argv[argv.index("--") + 1:]

addon_path = argv[0]
addon_name = argv[1]
addons_dir = os.path.join(bpy.utils.script_path_user(), "addons", addon_name)

copy_tree(addon_path, addons_dir)

addon_utils.enable(addon_name)
bpy.ops.wm.save_userpref()