from PIL import Image
from PIL.Image import Image as PIL_Image
from PIL.PngImagePlugin import PngImageFile
from pylab import *
import os
import re

def is_right_to_left(load_path, prefix, W, H):
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

def generate_geni(load_path, save_path, ftxt, W, H, convert_to_rigth_to_left = False):
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

    files = os.listdir(load_path)
    probability_array: np.ndarray = np.zeros((200, 120))
    for i in range(1, len(files)+1):
        print('#' + str(i))
        txt = '{0:03d}'.format(i)
        name = '{0}/{1}-{2}.png'.format(load_path, ftxt, txt)
        img: Image.Image = Image.open(name)
        bbox = img.getbbox()
        silhouette = img.crop(bbox)
        silhouette = silhouette.resize((120, 200))
        silhouette_array = np.asarray(silhouette, dtype=float)/255.0
        probability_array += silhouette_array
    probability_array /= len(files)
    # compute GEnI
    h_array = np.zeros((200, 120))
    h_array -= probability_array * np.log2(probability_array)
    h_array = np.nan_to_num(h_array)
    h_array -= (1.0 - probability_array) * np.log2(1.0- probability_array)
    h_array = np.nan_to_num(h_array)

    g_array = h_array - h_array.min()
    g_array /= h_array.max() - h_array.min()
    g_array *= 255.0
    geni = Image.fromarray(g_array)
    geni = geni.convert('L')

    if convert_to_rigth_to_left:
        result = is_right_to_left(load_path, ftxt, W, H)
        if not result:
            geni = geni.transpose(Image.FLIP_LEFT_RIGHT)
    save_name = '{0}/geni_{1}.bmp'.format(save_path, ftxt)
    geni.save(save_name, 'bmp')






def process_all_geni():

    load_dir = "/home/dyschemist/Workspace/datasets/gait/casia/silhouettes"
    save_dir = "/home/dyschemist/Workspace/datasets/geni"
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
            generate_geni(load_path, save_dir, ftxt, W, H, convert_to_rigth_to_left=True)

process_all_geni()
