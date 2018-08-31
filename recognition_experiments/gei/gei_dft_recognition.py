from pylab import *
from PIL import Image,ImageFilter,ImageOps
import random
import os



M=8
S=2
set_printoptions(suppress=True, precision=3)
path = '/home/dyschemist/Workspace/datasets/gei'
vlist = list()
# list number of files
lst = os.listdir(path)
L = len(lst) #ilosc probek
for gei_file in lst:
    img: Image.Image = Image.open('{0}/{1}'.format(path, gei_file))
    W, H = img.size
    X = matrix(reshape(img.getdata(), (H, W)))
    #calculate sum of elements
    sum = 0.0
    for n in range(0, W):
        for m in range(0, H):
            sum += X[m, n]
    #calculate center point
    xc = 0.0
    yc = 0.0
    for n in range(0, W):
        for m in range(0, H):
            p = X[m, n]/float(sum)
            xc += p*n
            yc += p*m
    xc = int(xc)
    yc = int(yc)
    X[yc, xc] = 25
    # scan angles 0..359
    vec = zeros(360, float)
    for n in range(0, 360):
        a = (2.0 * math.acos(-1.0) / 360.0) * n
        c = math.cos(a)
        s = math.sin(a)
        xi = xc
        yi = yc
        r = 1.0
        while 0 <= int(xi) < W and 0 <= int(yi) < H:
            v = X[int(yi), int(xi)] / float(sum)
            vec[n] = vec[n] + v
            xi = xi + r * c
            yi = yi + r * s
    # plot(arange(0,360),vec,'b')
    # show()
    # vec=abs(fft(vec))
    vec = fft(vec)
    vec /= vec[0]
    vec = vec[S:S + M]
    subject_id = gei_file.split('_')[1].split('-')[0]
    vlist.append((subject_id, vec))

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