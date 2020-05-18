from skimage.measure import compare_ssim
import argparse
import imutils
import cv2


def get_similarity(first_image, second_image):
    # load the two input images
    image_a = cv2.imread(first_image)
    image_b = cv2.imread(second_image)

    if image_a is None:
        print("Couldn't load an image\n {0}".format(first_image))
        return 0

    if image_b is None:
        print("Couldn't load an image\n {0}".format(second_image))
        return 0

    if image_a.shape != image_b.shape:
        return 0
    
    # convert the images to grayscale
    gray_a = cv2.cvtColor(image_a, cv2.COLOR_BGR2GRAY)
    gray_b = cv2.cvtColor(image_b, cv2.COLOR_BGR2GRAY)

    # compute the Structural Similarity Index (SSIM) between the two
    # images, ensuring that the difference image is returned
    (score, diff) = compare_ssim(gray_a, gray_b, full=True)
    
    # 1 means identical
    return score

from pathlib import Path

empty_images_references = ['/backup/LEGO2/render/0901/0901_Bright Bluish Green_0_1587813128.png']
empty_renders_paths = []

empty_renders_dir = Path('/backup/LEGO2/empty_renders')
empty_renders_dir.mkdir(parents=True, exist_ok=True)

empty_paths = []
all_parts = sorted(Path('/backup/LEGO2/render').iterdir())

for part_dir in all_parts:
    print("Scanning {}".format(part_dir.name))
    if not any(part_dir.iterdir()):
        empty_paths.append(part_dir)
    else:
        for part in part_dir.iterdir():
            for empty_image_reference in empty_images_references:
                if get_similarity(str(part.absolute()), empty_image_reference) > 0.9999:    
                    empty_renders_paths.append(part.absolute())
                    break

with open('empty_parts.txt', 'w') as f:
    for path in empty_renders_paths:
        f.write("%s\n" % path)
        
with open('empty_paths.txt', 'w') as f:
    for path in empty_paths:
        f.write("%s\n" % path)

from shutil import copy

for empty_render_path in empty_renders_paths:
    parent_path = empty_renders_dir / empty_render_path.parent.name
    parent_path.mkdir(parents=True, exist_ok=True)
    copy(str(empty_render_path.absolute()), str(parent_path.absolute()))
