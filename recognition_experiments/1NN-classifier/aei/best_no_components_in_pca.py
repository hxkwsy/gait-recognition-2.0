from PIL import Image
from pylab import *
import numpy as np

import os


def gei_pca_recognition(n_components=30):
    '''

    :param n_components:
    :return:
    '''
    path = '/home/dyschemist/Workspace/datasets/aei'

    data = list()
    row_data = list()
    column_data = list()
    # list number of files
    lst = os.listdir(path)
    sample_count = len(lst) #ilosc probek
    #print('Data load started')
    for gei_file in lst:
        img: Image.Image = Image.open('{0}/{1}'.format(path, gei_file))
        ar = np.asarray(img)
        id = gei_file.split('_')[1].split('-')[0]
        data.append((id, ar))
        row_data.append((id, ar.flatten()))
        column_data.append((id, ar.flatten('F')))

    from sklearn.decomposition import PCA

    #print('Data load completed, no of samples {0}, of size {1}-{2}'.format(sample_count, ar.shape[0], ar.shape[1]))

    #print('Creating data matrix and performing pca')

    data_matrix = np.vstack([item[1] for item in row_data])
    #print('Data matrix created')
    pca = PCA(n_components=n_components)
    pca_data_matrix = pca.fit_transform(data_matrix)
    #print('PCA performed')

    from sklearn.preprocessing import MinMaxScaler

    scaler = MinMaxScaler()
    scaled_pca_data_matrix = scaler.fit_transform(pca_data_matrix)

    #print(norm(scaled_pca_data_matrix))

    ## assign data to subjects

    for i in range(0, sample_count):
        identifier = row_data[i][0]
        orig_data = row_data[i][1]
        row_data[i] = (identifier, orig_data, scaled_pca_data_matrix[i])

    ## compute distance matrix
    #print('Will now create distance matrix')
    maximal_distance = 0
    distance_matrix = np.zeros((sample_count, sample_count),float)
    for i in range(0, sample_count):
        vector_1 = row_data[i][2]
        for j in range(0, sample_count):
            vector_2 = row_data[j][2]
            dist = norm(vector_1-vector_2)
            distance_matrix[i, j] = dist
            if dist > maximal_distance:
                maximal_distance = dist

    ## normalize
    for i in range(0, sample_count):
        for j in range(0, sample_count):
            distance_matrix[i, j] = 1.0 - distance_matrix[i, j] / maximal_distance

    #print('[DONE]')

    ## recognition 1-NN

    success_count = 0

    for i in range(0, sample_count):
        #print('processing no.{0} assigned to subject {1}'.format(i, row_data[i][0]))
        best_match_id = 0
        best_match_dist = 1.0
        for j in range(0, sample_count):
            if i == j:
                continue
            if 1.0 - distance_matrix[i, j] < best_match_dist:
                best_match_dist = 1.0 - distance_matrix[i, j]
                best_match_id = j
        #print(str(i) + ' -> '+str(j))
        #print(row_data[i][0] + ' -> ' + row_data[best_match_id][0])
        if row_data[i][0] == row_data[best_match_id][0]:
            success_count += 1
    #print('Classification accuracy {0}%'.format(success_count/sample_count*100.0))
    return success_count/sample_count*100.0


results = list()

for i in range(1, 50):
    print('Processing with size {0}'.format(i))
    result = gei_pca_recognition(n_components=i)
    results.append(result)

for i in range(0, len(results)):
    print('size {0}, accuracy {1}'.format(i, results[i]))

