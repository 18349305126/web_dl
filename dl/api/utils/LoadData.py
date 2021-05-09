"""
@author: Annie
@software: PyCharm
@file: LoadData.py
@time: 2019/03/25 14:58
"""

import SimpleITK as sitk
import numpy as np
import tensorflow as tf
import os
import cv2
import pydicom


# 将mha文件里面的数组读取出来
def load_mha_volume_as_array(filename):
    img = sitk.ReadImage(filename)
    nda = sitk.GetArrayFromImage(img)
    return nda


def load_mha_position(filename):
    img = sitk.ReadImage(filename)
    z = img.GetOrigin()[2]
    spacing = img.GetSpacing()[2]
    return z, spacing


# 数据存储格式为：images/病例1.mhd 病例2.mhd ......
#              labels/病例1_segmentation.mhd 病例_segmentation.mhd ......
def data_generator_xd(raws_path, segs_path):
    x = []
    y = []
    file = os.listdir(raws_path)
    for filename in file:
        fname = os.path.splitext(filename)[0]
        # rpath = os.path.join(fname, fname) + '.mhd'
        r_nda3D = load_mha_volume_as_array(os.path.join(raws_path, fname+'.mhd'))  # 获取每个病例的3D数组
        s_nda3D = load_mha_volume_as_array(os.path.join(segs_path, fname+'_segmentation.mhd'))
        t = np.nonzero(s_nda3D)
        x1 = np.max(t[0])
        x2 = np.min(t[0])
        r_nda3D = r_nda3D[np.ix_(range(x2, x1),range(35, 291), range(127, 383))]  # range(b, a)
        s_nda3D = s_nda3D[np.ix_(range(x2, x1), range(35, 291), range(127, 383))]
        for n in range(r_nda3D.shape[0]):
        # for n in range(15, 90):
            x.append(r_nda3D[n])
            y.append(s_nda3D[n])

    return np.array(x), np.array(y)


#if __name__ == '__main__':
#     raws_path = 'D:\Contouring\Data\CT\T1\SY\mhd\images'
#     segs_path = 'D:\Contouring\Data\CT\T1\SY\mhd\labels'
#     x, y = data_generator_xd(raws_path, segs_path)


