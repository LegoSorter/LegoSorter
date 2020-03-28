import argparse
import os
import bpy
import sys
import math
from random import random


class SceneNotPreparedException(Exception):
    pass


class BrickRenderer:
    def __init__(self, part_path, ldraw_path, pattern_scene_path, resolution, output_path):
        self.__part_path = part_path
        self.__ldraw_path = ldraw_path
        self.resolution = resolution
        self.__pattern_scene_path = pattern_scene_path
        self.__brick_object = None
        self.output_path = output_path

    def load_pattern_scene(self):
        bpy.ops.wm.open_mainfile(filepath=self.__pattern_scene_path)

    def get_brick_object(self):
        if not self.__brick_object:
            raise SceneNotPreparedException()
        return self.__brick_object

    def import_brick_scene(self):
        bpy.ops.import_scene.importldraw(filepath=self.__part_path, ldrawPath=self.__ldraw_path,
                                         importCameras=False, positionCamera=False, addEnvironment=False)
        self.__brick_object = [x for x in bpy.data.objects if os.path.basename(self.__part_path) in x.name][0]

        set_object_position(self.__brick_object, 0, 0, 1.5 * self.__brick_object.location.z)
        set_object_rotation(self.__brick_object, random() * 360, random() * 360, random() * 360)

    def prepare_scene(self):
        self.load_pattern_scene()
        self.import_brick_scene()
        self.set_physics()
        self.__brick_object.active_material = bpy.data.objects["PatternBrick"].active_material

        bpy.context.window.scene = bpy.data.scenes["TargetScene"]
        bpy.context.scene.camera.location = (7.0, 0.0, 4.0)
        bpy.context.scene.collection.objects.link(self.__brick_object)
        return True

    def render(self, samples_count=1, transformation=None, **kwargs):
        part_name = os.path.basename(self.__part_path).split(".")[0]  # Extract part name
        bpy.context.scene.render.resolution_x, bpy.context.scene.render.resolution_y = self.resolution

        bpy.context.scene.camera = bpy.data.objects['Camera']
        bpy.context.scene.camera.data.sensor_fit = 'VERTICAL'
        bpy.context.scene.camera.data.lens = 15

        bpy.context.scene.cycles.device = 'GPU'
        # bpy.context.scene.render.engine = 'BLENDER_EEVEE'
        bpy.context.scene.render.engine = 'CYCLES'

        # bpy.context.scene.eevee.taa_render_samples = 256
        # bpy.context.scene.eevee.taa_samples = 64

        bpy.context.scene.cycles.samples = 50

        # Skip animation
        for i in range(0, 100):
            bpy.context.scene.frame_set(i)

        for i in range(samples_count):
            bpy.context.scene.render.filepath = os.path.join(self.output_path, "{:s}_{:d}.png".format(part_name, i))
            print("------------------------------------------")
            print("Rendering {} of {}".format(i, samples_count))
            print("------------------------------------------")
            bpy.ops.render.render(write_still=True)
            transformation(obj=self.get_brick_object(), **kwargs) if transformation \
                else print("Transformation not defined")
        return

    def set_physics(self):
        scene = bpy.data.scenes['TargetScene']
        bpy.context.window.scene = scene

        ground = scene.objects['Plane']
        ground.rigid_body.type = 'PASSIVE'
        ground.rigid_body.collision_shape = 'CONVEX_HULL'

        scene.rigidbody_world.collection.objects.link(self.__brick_object)
        bpy.ops.object.origin_set(type='GEOMETRY_ORIGIN', center='MEDIAN')
        self.__brick_object.rigid_body.collision_shape = 'CONVEX_HULL'
        self.__brick_object.rigid_body.type = 'ACTIVE'


def main(args):
    brickRender = BrickRenderer(args.part, args.ldraw, args.scene, (args.width, args.height),
                                args.output_dir)
    brickRender.prepare_scene()
    brickRender.render(samples_count=args.samples, transformation=shift_horizontally, shift=args.shift)


def shift_horizontally(obj, shift=None):
    # It's tricky to move an object which is animated so I move a whole world except this object in the opposite
    # direction
    for o in bpy.data.objects:
        if o.name != obj.name:
            o.location.x -= shift


def rotate_object(obj, x=0.0, y=0.0, z=0.0):
    obj.rotation_euler[0] += degree_to_pi(x)
    obj.rotation_euler[1] += degree_to_pi(y)
    obj.rotation_euler[2] += degree_to_pi(z)


def set_object_rotation(obj, x=0.0, y=0.0, z=0.0):
    obj.rotation_euler[0] = degree_to_pi(x)
    obj.rotation_euler[1] = degree_to_pi(y)
    obj.rotation_euler[2] = degree_to_pi(z)
    print("Object rotation set to {} {} {}".format(obj.rotation_euler[0], obj.rotation_euler[1], obj.rotation_euler[2]))


def set_object_position(obj, x=0.0, y=0.0, z=0.0):
    obj.location = (x, y, z)


def degree_to_pi(degrees):
    return 2 * degrees / 360.0 * math.pi


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--width", type=int, help="width of an output image", default=300)
    parser.add_argument("--height", type=int, help="height of an output image", default=300)
    parser.add_argument("--part", help="a path to the part to be rendered", required=True)
    parser.add_argument("--output_dir", help="a path to the output directory", required=True)
    parser.add_argument("--ldraw", help="a path to the ldraw library", required=True)
    parser.add_argument("--scene", help="a path to the pattern scene", required=True)
    parser.add_argument("--samples", type=int, help="how many images to render", default=10)
    parser.add_argument("--shift", type=float, help="block shift per sample", default=-0.1)

    arguments = parser.parse_args(sys.argv[sys.argv.index("--") + 1:])

    main(arguments)