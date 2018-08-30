from PIL import Image
from PIL.Image import Image as PIL_Image
from PIL.PngImagePlugin import PngImageFile
from pylab import *
import os
import re


def is_right_to_left(load_path, prefix, W, H):
    N = 352
    M = 240
    lst = os.listdir(load_path)
    # we will load firts and the last image
    first: PIL_Image = Image.open('{0}/{1}-{2}.png'.format(load_path,prefix,'{0:03d}'.format(1)))
    first_bbox = first.getbbox()
    last: PIL_Image = Image.open('{0}/{1}-{2}.png'.format(load_path, prefix, '{0:03d}'.format(len(lst))))
    last_bbox = last.getbbox()
    first_left = first_bbox[0]
    first_right = first_bbox[2]
    last_left = last_bbox[0]
    last_right = last_bbox[2]
    result = None
    if first_left > last_right:
        result = True
    if first_right < last_left:
        result = False

    return result

# load_path = '/home/dyschemist/Workspace/datasets/gait/casia/silhouettes/fyc/00_1'
# prefix = 'fyc-00_1'
# load_path2 = '/home/dyschemist/Workspace/datasets/gait/casia/silhouettes/fyc/00_2'
# prefix2 = 'fyc-00_2'
# W = 88
# H = 160
#
# result1 = is_right_to_left(load_path, prefix, W, H)
# result2 = is_right_to_left(load_path2, prefix2, W, H)
#
# print('Result 1 : {0}\nResult 2 : {1}'.format(result1, result2))

def generate_gei(load_path, save_path, ftxt, W, H, convert_to_rigth_to_left = False):
    '''
    function creates gei image a sequence of images
    :param load_path:  path to a dir with images
    :param save_path: path to save a final gei image
    :param ftxt: identifier to a sample
    :param W: image width
    :param H: image height
    :param convert_to_rigth_to_left: if true script will try to detect movement from left to right and flip direction
            in final gei
    :return: None
    '''
    N = 352
    M = 240
    L = 75
    T = 10
    F = 10
    lst = os.listdir(load_path)
    slst = list()
    for i in range(1, len(lst)+1):
        print('#' + str(i))
        txt = '{0:03d}'.format(i)
        name = '{0}/{1}-{2}.png'.format(load_path, ftxt, txt)
        #name = path + '\\' + ftxt + '-' + txt + '.png'
        img = Image.open(name)
        X = matrix(reshape(img.getdata(), (M, N)))

        hh = zeros(N, float)
        hv = zeros(M, float)
        for j in range(0, N):
            hh[j] = sum(X[:, j]) / 255.0
        for j in range(0, M):
            hv[j] = sum(X[j, :]) / 255.0
        # find x limits

        minx = 0
        maxx = 0
        for j in range(0, N):
            if hh[j] > T:
                minx = j - F
                break
        for j in range(0, N):
            if hh[N-j-1] > T:
                maxx = N - j - 1 + F
                break
        miny = 0
        maxy = 0
        # find y limits
        for j in range(0, M):
            if hv[j] > T:
                miny = j-F
                break
        for j in range(0, M):
            if hv[M-j-1]:
                maxy = M - j - 1 + F
                break
        if minx < 0:
            minx = 0
        if maxx > N-1:
            maxx = N-1
        if miny < 0:
            miny = 0
        if maxy > M-1:
            maxy = M-1
        print('minx=' + str(minx) + ' maxx=' + str(maxx))
        print('miny=' + str(miny) + ' maxy=' + str(maxy))
        xc = 0.0
        yc = 0.0
        num = 0
        for n in range(minx, maxx + 1):
            for m in range(miny, maxy + 1):
                if X[m, n] > 0:
                    xc = xc + n
                    yc = yc + m
                    num = num + 1
        xc = int(xc / float(num))
        yc = int(yc / float(num))
        Y = copy(X[miny:maxy + 1, minx:maxx + 1])
        slst.append([Y, [xc - minx, yc - miny]])
        print('xc=' + str(xc - minx) + ' yc=' + str(yc - miny))
    width = 0
    height = 0
    lx = 0
    rx = 0
    ty = 0
    by = 0
    for i in range(0, len(slst)):
        t = slst[i]
        X = copy(t[0])
        [h, w] = shape(X)
        [xc, yc] = t[1]
        if xc > lx:
            lx = xc
        if w - xc > rx:
            rx = w - xc
        if yc > ty:
            ty = yc
        if h - yc > by:
            by = h - yc
        if w > width:
            width = w
        if h > height:
            height = h
    width = lx + rx
    height = ty + by
    print(' width=' + str(width))
    print('height=' + str(height))
    xxc = lx + (width - (rx + lx)) // 2
    yyc = ty + (height - (by + ty)) // 2
    print('xxc=' + str(xxc))
    print('yyc=' + str(yyc))
    GEI = zeros((height, width), float)
    for i in range(0, len(slst)):
        t = slst[i]
        X = copy(t[0])
        [h, w] = shape(X)
        [xc, yc] = t[1]
        for n in range(0, w):
            for m in range(0, h):
                i1 = (xxc - xc) + n
                i2 = (yyc - yc) + m
                GEI[i2, i1] = GEI[i2, i1] + X[m, n]
    mval = 0
    for i in range(0, width):
        for j in range(0, height):
            if GEI[j, i] > mval:
                mval = GEI[j, i]
    X = zeros((height, width), uint8)
    for i in range(0, width):
        for j in range(0, height):
            b = int(255.0 * GEI[j, i] / mval)
            if b < 0:
                b = 0
            if b > 255:
                b = 255
            X[j, i] = uint8(b)
    im = Image.fromarray(X)
    im2 = im.resize((W, H), Image.ANTIALIAS)
    if convert_to_rigth_to_left:
        result = is_right_to_left(load_path, ftxt, W, H)
        if not result:
            im2 = im2.transpose(Image.FLIP_LEFT_RIGHT)
    save_name = '{0}/gei_{1}.bmp'.format(save_path, ftxt)
    im2.save(save_name, 'bmp')


def process_all_gei():

    load_dir = "/home/dyschemist/Workspace/datasets/gait/casia/silhouettes"
    save_dir = "/home/dyschemist/Workspace/datasets/gei"
    W = 88
    H = 160
    pattern = re.compile('00_*')
    for dir in os.listdir(load_dir):
        for sample in os.listdir('{0}/{1}'.format(load_dir, dir)):
            if not pattern.match(sample):
                continue
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)
            load_path = '{0}/{1}/{2}'.format(load_dir, dir, sample)
            ftxt = '{0}-{1}'.format(dir, sample)
            generate_gei(load_path, save_dir, ftxt, W, H,convert_to_rigth_to_left=True)

process_all_gei()