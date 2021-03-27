import os
import argparse
from matplotlib import pyplot as plt

from utils.manage import Files
from image.process import Image
from image.analysis import Annotations

parser = argparse.ArgumentParser(description="Annotate images execute with python -i ...")
parser.add_argument("image" , type=str, help="path to image")
parser.add_argument("db" , type=str, help="path to annotations database")
parser.add_argument("analysis", type=str, help="applied analysis, this was usually specified in the detection arguments")
parser.add_argument("-p", "--plot" , type=str, help="specify type of plot, select from: 1) plot_complete_tag_diff 2) plot_tag 3) plot_tag_diff", default="plot_tag")
parser.add_argument("-s", "--settings" , type=str, help="path to settings file", default="annotations_default.json")
args = parser.parse_args()

sdir = Files.load_settings_dir()
settings = Files.read_settings(os.path.join(sdir, args.settings))

print("working on image:", args.image)
print("annotating analysis:", args.analysis)
print("storing output in:", args.db)
print("using settings:", settings)

# open series and load image
i = Image(args.image, ignore_struct_path=True, import_image=False)

a = Annotations(i, args.analysis, tag_db_path=args.db, keymap=settings["keymap"])

a.load_processed_tags()
a.start(plot_type=args.plot)
# a.set_plot_titles()
a.show_tag_number(0)
# plt.show()

