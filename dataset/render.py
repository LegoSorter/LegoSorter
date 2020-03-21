import argparse
import os
import bpy
import sys
import math


def main(args):
    obj = import_part(args.part, args.ldraw)
    arrange_world(args)
    render(obj, args)


def import_part(part_path, ldraw_path):
    bpy.ops.import_scene.importldraw(filepath=part_path, ldrawPath=ldraw_path)

    objects = [x for x in bpy.data.objects if os.path.basename(part_path) in x.name]
    return objects[0]


def rotate_object(obj, x=0.0, y=0.0, z=0.0):
    obj.rotation_euler[0] += degree_to_pi(x)
    obj.rotation_euler[1] += degree_to_pi(y)
    obj.rotation_euler[2] += degree_to_pi(z)


def set_object_rotation(obj, x=0.0, y=0.0, z=0.0):
    obj.rotation_euler[0] = degree_to_pi(x)
    obj.rotation_euler[1] = degree_to_pi(y)
    obj.rotation_euler[2] = degree_to_pi(z)


def arrange_world(args):
    # TODO: set up world
    return


def degree_to_pi(degrees):
    return 2 * degrees / 360.0 * math.pi


def render(obj, args):
    part_name = os.path.basename(args.part).split(".")[0]  # Extract part name

    # TODO: set render options
    set_object_rotation(obj, args.rotation_x, args.rotation_y, args.rotation_z)

    bpy.context.scene.render.resolution_x = args.width
    bpy.context.scene.render.resolution_y = args.height
    bpy.context.scene.cycles.device = 'GPU'
    bpy.context.scene.cycles.samples = 10

    for i in range(args.samples):
        bpy.context.scene.render.filepath = os.path.join(args.output_dir, "{:s}_{:d}.png".format(part_name, i))
        print("------------------------------------------")
        print("Rendering {} of {}".format(i, args.samples))
        print("------------------------------------------")
        bpy.ops.render.render(write_still=True)
        rotate_object(obj, args.delta_x, args.delta_y, args.delta_z)
    return


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--width", type=int, help="width of an output image", default=300)
    parser.add_argument("--height", type=int, help="height of an output image", default=300)
    parser.add_argument("--part", help="a path to the part to be rendered", required=True)
    parser.add_argument("--output_dir", help="a path to the output directory", required=True)
    parser.add_argument("--ldraw", help="a path to the ldraw library", required=True)
    parser.add_argument("--samples", type=int, help="how many images to render", default=10)
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
