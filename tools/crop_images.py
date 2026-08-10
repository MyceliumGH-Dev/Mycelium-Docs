"""Trim the uniform canvas background off each exported component screenshot.

    python tools/crop_images.py docs

Writes `<name>-crop.png` next to each `<name>.png` in docs/images/components/; the
component pages reference the cropped variant (USE_CROPPED_IMAGES in export_components.py).

Requires Pillow: pip install pillow
"""

import concurrent.futures
import glob
import os
import sys

from PIL import Image, ImageChops

PAD = 20


def crop_image(file_path):
    try:
        if file_path.endswith("-crop.png"):
            return

        orig_img = Image.open(file_path).convert("RGBA")
        rgb_img = orig_img.convert("RGB")

        # The canvas paints a uniform background, so the top-left pixel is the key colour.
        bg_color = rgb_img.getpixel((0, 0))
        bg = Image.new("RGB", rgb_img.size, bg_color)

        bbox = ImageChops.difference(rgb_img, bg).getbbox()
        if not bbox:
            return

        left, top, right, bottom = bbox
        left = max(0, left - PAD)
        top = max(0, top - PAD)
        right = min(orig_img.width, right + PAD)
        bottom = min(orig_img.height, bottom + PAD)

        orig_img.crop((left, top, right, bottom)).save(
            file_path.replace(".png", "-crop.png"))
    except Exception as e:
        print("Failed to crop %s: %s" % (os.path.basename(file_path), e))


def main():
    if len(sys.argv) < 2:
        print("Usage: python crop_images.py <docsFolder>")
        sys.exit(1)

    target_dir = os.path.join(sys.argv[1], "images", "components")
    if not os.path.exists(target_dir):
        print("Directory %s not found." % target_dir)
        sys.exit(1)

    files = [f for f in glob.glob(os.path.join(target_dir, "*.png"))
             if not f.endswith("-crop.png")]

    print("Found %d images to crop. Starting parallel crop..." % len(files))
    with concurrent.futures.ProcessPoolExecutor() as executor:
        executor.map(crop_image, files)
    print("Cropping complete!")


if __name__ == "__main__":
    main()
