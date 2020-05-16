from skimage.measure import compare_ssim
import argparse
import imutils
import cv2


def get_similarity(first_image, second_image):
    # load the two input images
    imageA = cv2.imread(first_image)
    imageB = cv2.imread(second_image)
    
    if imageA.shape != imageB.shape:
        return 0
    
    # convert the images to grayscale
    grayA = cv2.cvtColor(imageA, cv2.COLOR_BGR2GRAY)
    grayB = cv2.cvtColor(imageB, cv2.COLOR_BGR2GRAY)
    
    # compute the Structural Similarity Index (SSIM) between the two
    # images, ensuring that the difference image is returned
    (score, diff) = compare_ssim(grayA, grayB, full=True)
    
    # 1 means identical
    return score

from pathlib import Path

empty_images_references = ['/backup/LEGO2/render/0901/0901_Dark Brown_0_1587327027.png', '/backup/LEGO2/render/0901/0901_Bright Blue_0_1587483388.png']
empty_renders_paths = []

empty_renders_dir = Path('/backup/LEGO2/empty_renders')
empty_renders_dir.mkdir(parents=True, exist_ok=True)

empty_paths = []

for part_dir in Path('/backup/LEGO2/render').iterdir():
    print("Scanning {}".format(part_dir.name))
    if not any(part_dir.iterdir()):
        empty_paths.append(part_dir)
    else:
        for part in part_dir.iterdir():
            for empty_image_reference in empty_images_references:
                if get_similarity(str(part.absolute()), empty_image_reference) > 0.9999:    
                    empty_renders_paths.append(part.absolute())

with open('empty_parts.txt', 'w') as f:
    for path in empty_render_paths:
        f.write("%s\n" % path)
        
with open('empty_paths.txt', 'w') as f:
    for path in empty_paths:
        f.write("%s\n" % path)

from shutil import copy

for empty_render_path in empty_renders_paths:
    parent_path = empty_renders_dir / empty_render_path.parent.name
    parent_path.mkdir(parents=True, exist_ok=True)
    copy(str(empty_render_path.absolute()), str(parent_path.absolute()))
