from PIL import Image
from pylab import *
import numpy as np

import cv2
import re
import os

def is_right_to_left(load_path)-> bool:
    files = os.listdir(load_path)
    files.sort()
    files_length = len(files)
    first_file = files[0]
    last_file = files[files_length-1]
    first: Image.Image = Image.open('{0}/{1}'.format(load_path, first_file))
    bbox_first = first.getbbox()
    last: Image.Image = Image.open('{0}/{1}'.format(load_path,last_file))
    bbox_last = last.getbbox()
    first_left = bbox_first[0]
    first_right = bbox_first[2]
    last_left = bbox_last[0]
    last_right = bbox_last[2]
    result = None
    if first_left > last_right:
        result = True
    if first_right < last_left:
        result = False

    return result

def load_gait_sequence(load_path):
    files = os.listdir(load_path)
    files.sort()
    max_width_stride = 0
    sum_array = np.zeros(120*209)
    for file in files:
        full_path = '{0}/{1}'.format(load_path, file)
        img: Image.Image = Image.open(full_path)
        # check stride
        bbox = img.getbbox()
        stride = bbox[2]-bbox[0]
        if stride > max_width_stride:
            max_width_stride = stride
        # get vector of image
        silhouette = img.crop(bbox)

        silhouette = silhouette.resize((120, 209))
        temp_array = np.asarray(silhouette, dtype=float)
        array = temp_array.flatten()/255.0
        sum_array += array
    sequence_length = len(files)
    sum_array /= sequence_length
    sum_array *= 255
    sum_array = sum_array.astype(uint8)
    return max_width_stride, sum_array


input_path = '/home/dyschemist/Workspace/datasets/gait/casia/silhouettes'

matching_pattern = '00_*'
regex = re.compile(matching_pattern)

print('Data loading ...')

subjects = os.listdir(input_path)
data_container = list()
for subject in subjects:
    subdir = '{0}/{1}'.format(input_path, subject)
    sequences = os.listdir(subdir)
    for sequence in sequences:
        if not regex.match(sequence):
            continue
        sequence_dir = '{0}/{1}'.format(subdir, sequence)
        if not is_right_to_left(sequence_dir):
            continue
        stride, data = load_gait_sequence(sequence_dir)
        data_container.append( (subject, sequence, stride, data))

print('Data loading - [DONE]')


