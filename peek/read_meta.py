import argparse
import os
from glob import glob
from peek.image.analysis import Data


parser = argparse.ArgumentParser(description='Carry out object detection on two images of a Series')
parser.add_argument('input' , type=str, help='root directory to metafiles or complete file path of meta file')
parser.add_argument('-d', '--date', type=str, help='date of meta files', default="*")
parser.add_argument('-n', '--nano_id', type=str, help='id of nano of meta files', default="*")
parser.add_argument('-o', '--output_dir', type=str, help='storage location of meta file', default="")
args = parser.parse_args()


# get all json files
paths = glob(os.path.join(args.input, args.date, args.nano_id, "*", "") + "*.json")
meta = Data.collect_meta(paths)

if args.output_dir == "":
    storage = os.path.dirname(args.input)
else:
    storage = args.output_dir

fname = "_".join((args.date, args.nano_id, "meta.csv")).replace("*", "all")

meta.to_csv(os.path.join(storage, fname), index=True)

