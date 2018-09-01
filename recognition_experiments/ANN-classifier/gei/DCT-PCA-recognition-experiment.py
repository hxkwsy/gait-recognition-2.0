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
        data_container.append([subject, sequence, stride, data])

print('Data loading - [DONE]')
print('DCT feature extraction ...')
from scipy.fftpack import dct

from sklearn.preprocessing import MinMaxScaler

data_container_size = len(data_container)
for i in range(0, data_container_size):
    dct_transformed_data = dct(data_container[i][3])
    dct_transformed_data = dct_transformed_data[0:3900]
    data_container[i].append(dct_transformed_data)

print('DCT feature extraction - DONE')

print('PCA dimensionality reduction ...')

from sklearn.decomposition import PCA
n_components = 7
pca = PCA(n_components=n_components)

data_matrix = np.zeros( (data_container_size, 3900))

for i in range(0, data_container_size):
    data_matrix[i, :] = data_container[i][4]

pca_data_matrix = pca.fit_transform(data_matrix)

print('PCA dimensionality reduction DONE')

#generate y for ANN training

subject_to_code = {}
current_code_counter = 0
for element in data_container:
    if not element[0] in subject_to_code:
        subject_to_code[element[0]] = current_code_counter
        current_code_counter += 1

no_of_subjects = len(subject_to_code)

y = np.zeros((data_container_size))

for i in range(0, data_container_size):
    subject = data_container[i][0]
    y[i] = subject_to_code[subject]

print('ANN recognition ...')

from sklearn.neural_network import MLPClassifier

nn = MLPClassifier(solver='lbfgs', alpha=1e-5, hidden_layer_sizes=(10,10,10,10,10,10,10,10,10,10,10,10,10,10, ))

print('Training started')

nn.fit(pca_data_matrix, y)

print('Training is done')

correct_recognition = 0
for i in range(0, data_container_size):
    x = pca_data_matrix[i, :]
    result = nn.predict([x])
    if result == subject_to_code[data_container[i][0]]:
        correct_recognition += 1

print('Accuracy {0}%'.format(correct_recognition/data_container_size*100.0))

# print('ANN recognition DONE')