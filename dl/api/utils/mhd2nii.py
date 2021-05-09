import os
import SimpleITK as sitk
import numpy as np
from api.utils.config import Config as cfg


# 将mhd文件里面的数组读取出来
def load_mhd_volume_as_array(filename):
    img = sitk.ReadImage(filename)
    nda = sitk.GetArrayFromImage(img)
    return nda


def mkdir(path):
    path = path.strip() # 去除空格
    path = path.rstrip("\\")# 去除尾部 \ 符号
    isExists = os.path.exists(path) # 判断路径是否存在
    if not isExists:
        os.makedirs(path)# 如果不存在则创建目录
        return True
    else:
        return False # 如果目录存在则不创建


def dataChange(mhd_path, nii_path, suffix):
    filename = mhd_path.split('\\')[-1].split('.')[0]
    # print(filename)
    img = load_mhd_volume_as_array(mhd_path)
    sitk_img = sitk.GetImageFromArray(img, isVector=False)
    sitk.WriteImage(sitk_img, os.path.join(nii_path, filename + suffix))


def mhd2nii(mhd_dir, nii_dir):
    pathMHD = mhd_dir
    pathNII = nii_dir
    suffix = '.nii'
    ipathmhd = os.path.join(pathMHD,'images')
    lpathmhd = os.path.join(pathMHD,'labels')
    ipathnii = os.path.join(pathNII,'images')
    lpathnii = os.path.join(pathNII,'labels')
    mkdir(ipathnii)
    mkdir(lpathnii)
    for root, dirs, filenames in os.walk(ipathmhd):
        for name in filenames:
            paths = os.path.join(root, name)
            # print(paths)
            if ".mh" in ''.join(paths).lower():
                dataChange(paths, ipathnii, suffix)
            else:
                pass

    for root, dirs, filenames in os.walk(lpathmhd):
        for name in filenames:
            paths = os.path.join(root, name)
            # print(paths)
            if ".mh" in ''.join(paths).lower():
                dataChange(paths, lpathnii, suffix)
            else:
                pass

if __name__ == "__main__":
    mhd2nii()