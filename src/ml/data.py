import os
import imageio
import numpy as np
import pandas as pd

def load_images(path):
    content = os.scandir(path)
    images = []
    fnames = []

    for f in content:
        images.append(imageio.imread(f.path))
        fnames.append(f.name.split(".")[0])

    return images, fnames

def load_annotated_data(path_annotations, path_imgs, label_column="label", id_columns=[], add_data=[]):
    """
    this should be moderately versatile. If I create my annotations just like a
    Dataframe with two columns id and label where id corresponds to the file name
    of the image and label is the tag of the image, this works very simple
    """
    # read images
    images, fnames = load_images(path_imgs)

    # read annotations
    annotations = pd.read_csv(path_annotations, dtype=str)

    data = {
        "data": [],
        "labels":[]
        }

    if len(add_data) > 0:
        data.update({"additional_data":[]})
    
    # check if annotations and images have the same length
    assert len(images) == len(fnames) == annotations.shape[0], print("unequal length of data and annotations")

    # iterate over annotations table
    for _, a in annotations.iterrows():
        # create id column which should equal the file name of the images (omitting the file extension)
        a_id = "_".join(a.loc[id_columns])
        img = [i for i, f in zip(images, fnames) if f == a_id]

        # append data to lists
        data["data"].extend(img)
        data["labels"].append(a.loc[label_column])
        if len(add_data) > 0:
            data["additional_data"].append(a.loc[add_data])

    assert len(data["labels"]) == len(data["data"]), print("somefiles wer not found")

    data["data"] = np.array(data["data"])
    data["labels"] = np.array(data["labels"])

    return data
    