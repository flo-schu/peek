import os
import argparse
from peek.utils.manage import Files
from peek.image.analysis import Data
from peek.evaluation.main import analyse, save

parser = argparse.ArgumentParser(description='Carry out object detection on two images of a Series')
parser.add_argument('input' , type=str, help='path to images')
parser.add_argument('-i', '--id', type=str, help='Nanocosm ID', default='all')
parser.add_argument('-d', '--date', type=str, help='Measurement Date', default='all')
parser.add_argument('-n', '--number', type=str, help='Number of picture', default='all')
parser.add_argument('-s', '--settings', type=str, help='settings for evaluation', default='evaluate_default.json')
args = parser.parse_args()

print('reading parameters ...')
sdir = Files.load_settings_dir()
settings = Files.read_settings(os.path.join(sdir, args.settings))
print(settings)

# import image data
d = Data(args.input,
         search_keyword=settings["analysis"], 
         correct_path=settings["path_correction"])

# analyse(data=d, algorithm="count_and_average_over_id", plot="show_ts", sample_id="10")
analyse(data=d, 
        algorithm=settings["algorithm"], 
        plot=settings["plot"], 
        algoargs=settings["algoargs"],
        plotargs=settings["plotargs"],
        sample_id=args.id,
        date=args.date,
        img_num=args.number)

