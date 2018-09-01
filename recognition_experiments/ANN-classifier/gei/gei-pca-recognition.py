from PIL import Image
from pylab import *
import numpy as np

import os



path = '/home/dyschemist/Workspace/datasets/gei'

data = list()
row_data = list()
column_data = list()
# list number of files
lst = os.listdir(path)
lst.sort()
sample_count = len(lst) #ilosc probek
print('Data load started')
for gei_file in lst:
    img: Image.Image = Image.open('{0}/{1}'.format(path, gei_file))
    ar = np.asarray(img)
    id = gei_file.split('_')[1].split('-')[0]
    data.append((id, ar))
    row_data.append((id, ar.flatten()))
    column_data.append((id, ar.flatten('F')))

from sklearn.decomposition import PCA

print('Data load completed, no of samples {0}, of size {1}-{2}'.format(sample_count, ar.shape[0], ar.shape[1]))

print('Creating data matrix and performing pca')

data_matrix = np.vstack([item[1] for item in row_data])
print('Data matrix created')
pca = PCA(n_components= 10)
pca_data_matrix = pca.fit_transform(data_matrix)
print('PCA performed')

from sklearn.preprocessing import MinMaxScaler

scaler = MinMaxScaler()
scaled_pca_data_matrix = scaler.fit_transform(pca_data_matrix)

print(norm(scaled_pca_data_matrix))

## assign data to subjects

for i in range(0, sample_count):
    identifier = row_data[i][0]
    orig_data = row_data[i][1]
    row_data[i] = (identifier, orig_data, scaled_pca_data_matrix[i])

print('[DONE]')

## ANN - classifier

## generate y


subject_to_code = {}
current_code_counter = 0
for element in row_data:
    if not element[0] in subject_to_code:
        subject_to_code[element[0]] = current_code_counter
        current_code_counter += 1

y = np.zeros((sample_count))

for i in range(0, sample_count):
    subject = row_data[i][0]
    y[i] = subject_to_code[subject]

print(y)

print('ANN recognition ...')

from sklearn.neural_network import MLPClassifier

nn = MLPClassifier(solver='lbfgs', alpha=1e-5, hidden_layer_sizes=(10, 10, 10, 10, 10,  ), random_state=2)

print('Training started')

nn.fit(scaled_pca_data_matrix, y)

print('Training is done')

correct_recognition = 0
for i in range(0, sample_count):
    x = scaled_pca_data_matrix[i, :]
    result = nn.predict([x])
    if result == subject_to_code[row_data[i][0]]:
        correct_recognition += 1

print('Accuracy {0}%'.format(correct_recognition/sample_count*100.0))
