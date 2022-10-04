from glob import glob
from PIL import Image
import argparse

parser = argparse.ArgumentParser(description="Create animated development of nanos")
parser.add_argument("id", type=str, help="nano ID")
args = parser.parse_args()


def make_gif(id):
    frames = [Image.open(image) for image in glob("data/pics_classic/*/{}.jpg".format(int(args.id) * 3 - 2))]
    frames = [im.rotate(90, Image.NEAREST, expand = 1) for im in frames]
    frame_one = frames[0]
    frame_one.save("plots/nanogifs/{}.gif".format(args.id), format="GIF", append_images=frames,
                   save_all=True, duration=250, loop=0)
    
make_gif(id)