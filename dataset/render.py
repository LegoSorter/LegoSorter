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
        bpy.ops.import_scene.importldraw(filepath=self.__part_path, ldrawPath=self.__ldraw_path)
        self.__brick_object = [x for x in bpy.data.objects if os.path.basename(self.__part_path) in x.name][0]

        set_object_position(self.__brick_object, 0, 0, 1.5 * self.__brick_object.location.z)
        set_object_rotation(self.__brick_object, random() * 360, random() * 360, random() * 360)

    def prepare_scene(self):
        self.load_pattern_scene()
        self.import_brick_scene()
        self.set_physics()
        self.__brick_object.active_material = bpy.data.objects["PatternBrick"].active_material

        bpy.context.window.scene = bpy.data.scenes["TargetScene"]
        bpy.context.scene.collection.objects.link(self.__brick_object)
        return True

    def render(self, samples_count=1, transformation=None, **kwargs):
        part_name = os.path.basename(self.__part_path).split(".")[0]  # Extract part name
        bpy.context.scene.render.resolution_x, bpy.context.scene.render.resolution_y = self.resolution
        bpy.context.scene.cycles.device = 'GPU'
        bpy.context.scene.cycles.samples = 10

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
        bpy.ops.rigidbody.world_add()

        ground = scene.objects['Plane.001']
        bpy.context.view_layer.objects.active = ground

        # This usage of 'object_add' will initialize a list of objects for the rigid body world
        bpy.ops.rigidbody.object_add()
        ground.rigid_body.type = 'PASSIVE'

        scene.rigidbody_world.collection.objects.link(self.__brick_object)
        self.__brick_object.rigid_body.collision_shape = 'BOX'
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
    parser.add_argument("--delta_x", type=float, default=0.0,
                        help="degree by which to rotate the part after each sample in an X axis")
    parser.add_argument("--delta_y", type=float, default=0.0,
                        help="degree by which to rotate the part after each sample in a Y axis")
    parser.add_argument("--delta_z", type=float, default=0.0,
                        help="degree by which to rotate the part after each sample in a Z axis")
    parser.add_argument("--rotation_x", type=float, default=0.0, help="starting rotation for an X axis")
    parser.add_argument("--rotation_y", type=float, default=0.0, help="starting rotation for a Y axis")
    parser.add_argument("--rotation_z", type=float, default=0.0, help="starting rotation for a Z axis")

    arguments = parser.parse_args(sys.argv[sys.argv.index("--") + 1:])

    main(arguments)