import bpy
import sys

argv = sys.argv
argv = argv[argv.index("--") + 1:]

file_path = argv[0]
output_path = argv[1]
ldraw_path = argv[2]

bpy.ops.import_scene.importldraw(filepath=file_path, ldrawPath=ldraw_path)
bpy.context.scene.cycles.device = 'GPU'
bpy.context.scene.cycles.samples = 20
bpy.context.scene.render.resolution_x = 200
bpy.context.scene.render.resolution_y = 100
bpy.context.scene.render.filepath = output_path
bpy.ops.render.render(write_still=True)
