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
parser.add_argument('-r', '--data_dir' , type=str, help='remote root of the image project data', default='/work/schunckf/nanocosm')
parser.add_argument('-n', '--nrows' , type=int, help='number of rows to be read', default=None)
parser.add_argument('-s', '--separator' , type=str, help='separator for rows', default=',')
parser.add_argument('-e', '--error_id' , type=str, help='id of images where qr code could not be read (name of folder)', default='999')
parser.add_argument('-i', '--struct_name' , type=str, help='file appendix for struct items, where image meta data are stored', default='_struct.json')
args = parser.parse_args()


qr = pd.read_table(args.input, sep=args.separator, names=['path','id_correct'], nrows=args.nrows)
for i, row in qr.iterrows():
    path = row.path

    # add correct filename ending to old corrections
    if "_qr.jpeg" not in path:
        path = path.replace(".jpeg", "_qr.jpeg")

    # prepend to data dir to path if the path is not absolute and the data_dir
    # prefix is  not in path
    if args.data_dir not in path and not os.path.isabs(path):
        path = os.path.join(args.data_dir, path)
        print(path)

    if not os.path.exists(path):
        print("no QR problem with", path)
        continue
    # read paths and edit paths
    p = os.path.normpath(os.path.dirname(path))
    f = os.path.basename(path).replace('.jpeg', '')
    if "_qr" in f:
        f = f.replace("_qr","")
    print('working in:', p, '-- on image:', f)
    
    ossep = os.path.sep
    pnew = p.replace(
        ossep + args.error_id + ossep, 
        ossep + str(row.id_correct).zfill(2) + ossep)
    
    # file paths
    files = [file for file in os.listdir(p) if f in file]
    pj = os.path.join(p, f + '_struct.json')
    # edit meta file file
    with open(pj, 'r') as file:
        meta = json.load(file)

    meta['id'] = str(int(row.id_correct)).zfill(2)
    meta['path'] = os.path.join(pnew, f + '.tiff')
    with open(pj, 'w') as file:
        json.dump(meta, file)
        
    # print('staged for move:', files)
    # create new directory and move files
    os.makedirs(pnew, exist_ok=True)
    print('created dir:', pnew)
    for f in files:
        fold = os.path.join(p, f)
        fnew = os.path.join(pnew, f)
        shutil.move(fold, fnew)
        print('moved', f, "to", fnew)
    # shutil.move(pj, pnew)


# qr['path'] = qr['path', 'id_correct'].apply(lambda x: re.sub('999',str(x[1]),x[0]))

# with open(args.input, 'r') as f:
#     qr = f.read()
# print(qr)
