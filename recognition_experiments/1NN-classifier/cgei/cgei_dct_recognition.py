from pylab import *
from PIL import Image,ImageFilter,ImageOps
import random
import os


def dctII(n):
    u=zeros((n, n), float64)
    v=1.0/sqrt(2.0)
    for i in range(0, n):
        for j in range(0, n):
            u[i][j] = v*math.sqrt(2.0/n)*cos(pi/n*i*(j+0.5))
        v = 1.0
    return matrix(u)

M=8
S=2
set_printoptions(suppress=True, precision=3)
path = '/home/dyschemist/Workspace/datasets/cgei'
vlist = list()
# list number of files
lst = os.listdir(path)
L = len(lst) #ilosc probek
for gei_file in lst:
    img: Image.Image = Image.open('{0}/{1}'.format(path, gei_file))
    W, H = img.size
    X = matrix(reshape(img.getdata(), (H, W)))
    U1 = matrix(dctII(H))
    U2 = matrix(dctII(W))
    Y = U1* X * U2.T
    vec = reshape(Y[S:S+M, S:S+M], M*M)
    id = gei_file.split('_')[1].split('-')[0]
    vlist.append((id, vec))

md = 0 #maximal distance
CM = matrix(zeros((L, L), float)) #macierz odleglości par wzorców
for i in range(0, L):
    vec1 = (vlist[i])[1]
    for j in range(0, L):
        vec2 = (vlist[j])[1]
        d = norm(vec1-vec2)
        CM[i, j] = d
        if d > md:
            md = d
## normalize
for i in range(0, L):
    for j in range(0, L):
        CM[i, j] = 1.0 - CM[i, j]/md

## classification
nc = 0
for i in range(0, L):
    print('processing no.{0} assigned to subject {1}'.format(i, vlist[i][0]))
    mini = 0
    minv = 1.0
    for j in range(0, L):
        if i == j:
            continue
        if 1.0 - CM[i, j] < minv :
            minv = 1.0 - CM[i, j]
            mini = j
    print(str(i) + ' -> ' + str(mini))
    print(vlist[i][0] + ' -> ' + vlist[mini][0])
    if vlist[i][0] == vlist[mini][0]:
        nc += 1
print('class. accuracy='+str(100.0*nc/L)+' %')
imshow(CM)
show()