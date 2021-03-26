import os
import imageio

def load_images(path):
    content = os.scandir(path)
    images = []
    fnames = []

    for f in content:
        images.append(imageio.read(os.path.join(path, f)))
        fnames.append(f.name.split(".")[0])

    return images, fnames