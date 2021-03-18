# 1. [x] get directory tree of all 999 subfolders
# 2. [x] read images
# 3. [x] downscale and cut out region where number of nano will be 
# 4. [ ] annotate with date, time and img name
# 5. [x] save and label according to date, time and name in one folder
# 6. [x] create CSV file with labels friom (5) in the same order (should be automatic due to date and time format YYYYMMDD_HHMM_NAME.tiff)
#    [ ] this should be kept and only updated with new unclear nanos, so that not everything has to be ran twice
# 7. [ ] read the file and move images from 999 to appropriate locations
from image.process import Image
from utils.manage import Files
import pandas as pd
import shutil
import json
import argparse
import os
import re

parser = argparse.ArgumentParser(description='Carry out object detection on two images of a Series')
parser.add_argument('input' , type=str, help='csv or txt file with original path and the corrected id')
parser.add_argument('-n', '--nrows' , type=str, help='number of rows to be read', default=None)
parser.add_argument('-s', '--separator' , type=str, help='separator for rows', default=',')
parser.add_argument('-e', '--error_id' , type=str, help='id of images where qr code could not be read (name of folder)', default='999')
parser.add_argument('-i', '--struct_name' , type=str, help='file appendix for struct items, where image meta data are stored', default='_struct.json')
args = parser.parse_args()


qr = pd.read_table(args.input, sep=args.separator, names=['path','id_correct'], nrows=args.nrows)
for i, row in qr.iterrows():
    # read paths and edit paths
    p = os.path.normpath(os.path.dirname(row.path))
    print(p)
    f = os.path.basename(row.path).replace('.jpeg', '')
    ossep = os.path.sep
    pnew = p.replace(
        ossep + args.error_id + ossep, 
        ossep + str(row.id_correct).zfill(2) + ossep)
    print(pnew)
    # edit meta file file
    pj = os.path.join(p, f + '_struct.json')
    with open(pj, 'r') as file:
        meta = json.load(file)

    print(meta)
    meta['id'] = str(row.id_correct).zfill(2)
    meta['path'] = os.path.join(pnew, f + '.tiff')
    print(meta)
    with open(pj, 'w') as file:
        json.dump(meta, file)

    # move the whole directory
    shutil.move(p, pnew)


# qr['path'] = qr['path', 'id_correct'].apply(lambda x: re.sub('999',str(x[1]),x[0]))

# with open(args.input, 'r') as f:
#     qr = f.read()
# print(qr)
