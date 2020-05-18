import glob
import os
from pathlib import Path
import random
import cv2

input_path = Path('input')
out_path = Path("dataset")

DISTRIBUTION = {
    "train": 80,
    "val": 20,
}


def crop_image_and_copy(img_path, dst_path, resolution=(300, 300)):
    # print(img_path.absolute())

    img = cv2.imread(str(img_path.absolute()))
    t_w, t_h = resolution
    c_w, c_h, _ = img.shape
    if t_w != c_w or t_h != c_h:
        left = round((c_w - t_w) / 2)
        top = round((c_h - t_h) / 2)
        crop_img = img[top:c_h + top, left:c_w + left]
    else:
        crop_img = img
    cv2.imwrite(str(dst_path.absolute()), crop_img)


class_list = [classname.name for classname in input_path.iterdir()]

for cls in class_list:
    files = [classname for classname in input_path.joinpath(cls).iterdir()]
    random.shuffle(files)
    dist = {
        "train": files[0:DISTRIBUTION["train"]],
        "val": files[DISTRIBUTION["train"]:DISTRIBUTION["train"] + DISTRIBUTION["val"]],
        "test": files[DISTRIBUTION["train"] + DISTRIBUTION["val"]:]
    }
    for type in dist:
        for image in dist[type]:
            brick_id = image.absolute().parent.name
            img_name = image.name

            dst_path = out_path.joinpath(type).joinpath(brick_id).joinpath(img_name)
            dst_path.parent.mkdir(parents=True, exist_ok=True)
            crop_image_and_copy(image, dst_path)
