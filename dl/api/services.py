import os

from api.utils.dcm2mhd import dcm2mhd
from api.utils.dcm2nii import dcm2nii
from api.utils.dcm2mha import dcm2mha
from api.utils.dcm2niigz import dcm2niigz
from api.utils.mhd2nii import mhd2nii
from api.utils.mha2nii import mha2nii
from api.utils.segcut import segCut
from api.utils.train import train
from api.utils.test import test
from api.common.validator import mhd_validator
from api.common.validator import mha_validator
from api.common.logger import logger


class TransformService():
    """
    数据转换组件的业务层
    """
    @staticmethod
    def dcm2mhd(dcm_dir, mhd_dir, seg_path, category):

        dcm2mhd(dcm_dir, mhd_dir, seg_path, category)

        list = []  # 定义一个列表，用来存储结果
        if (os.path.exists(dcm_dir)):  # 判断路径是否存在
            files = os.listdir(dcm_dir)  # 获取该目录下的所有文件或文件夹目录
            # print(files)
            for file in files:
                m = os.path.join(dcm_dir, file)  # 得到该文件下所有目录的路径
                if (os.path.isdir(m)):  # 判断该路径下是否是文件夹
                    if 'seg' in m.lower():
                        pass
                    else:
                        h = os.path.split(m)
                        list.append(h[1])
        for pathi in list:
            mhd_filename = mhd_dir + '/images/' + pathi.split('/')[-1] + '.mhd'
            is_mhd = mha_validator(mhd_filename)

        if not is_mhd:
            logger.warning("Mhd转换失败")
        return is_mhd, mhd_filename

    @staticmethod
    def dcm2mha(dcm_dir, mha_dir, seg_path, category):
        dcm2mha(dcm_dir, mha_dir, seg_path, category)

        #for pathi in dcm_dir:
            #print(pathi)
            #mha_filename = mha_dir + '/images' + dcm_dir.split('/')[-1] + '.mha'
            #print(mha_filename)
            #is_mhd = mha_validator(mha_filename)
        list = []  # 定义一个列表，用来存储结果
        if (os.path.exists(dcm_dir)):  # 判断路径是否存在
            files = os.listdir(dcm_dir)  # 获取该目录下的所有文件或文件夹目录
            # print(files)
            for file in files:
                m = os.path.join(dcm_dir, file)  # 得到该文件下所有目录的路径
                if (os.path.isdir(m)):  # 判断该路径下是否是文件夹
                    if 'seg' in m.lower():
                        pass
                    else:
                        h = os.path.split(m)
                        list.append(h[1])
        for pathi in list:
            mha_filename = mha_dir + '/images/' + pathi.split('/')[-1] + '.mha'
            is_mha = mha_validator(mha_filename)
        #is_mhd=True,
        #mha_filename = 'D:/lyh/code/bishe/WebDL-master07/WebDL-master/data/test/mha/images/00C1193200.mha'
        if not is_mha:
            logger.warning("Mha转换失败")
        return is_mha, mha_filename

    @staticmethod
    def dcm2nii(dcm_dir, nii_dir, seg_path, category):
        dcm2nii(dcm_dir, nii_dir, seg_path, category)

        list = []  # 定义一个列表，用来存储结果
        if (os.path.exists(dcm_dir)):  # 判断路径是否存在
            files = os.listdir(dcm_dir)  # 获取该目录下的所有文件或文件夹目录
            # print(files)
            for file in files:
                m = os.path.join(dcm_dir, file)  # 得到该文件下所有目录的路径
                if (os.path.isdir(m)):  # 判断该路径下是否是文件夹
                    if 'seg' in m.lower():
                        pass
                    else:
                        h = os.path.split(m)
                        list.append(h[1])
        for pathi in list:
            nii_filename = nii_dir + '/images/' + pathi.split('/')[-1] + '.nii'
            is_nii = mha_validator(nii_filename)

        if not is_nii:
            logger.warning("nii转换失败")
        return is_nii, nii_filename

    @staticmethod
    def dcm2niigz(dcm_dir, niigz_dir, seg_path, category):
        dcm2niigz(dcm_dir, niigz_dir, seg_path, category)

        list = []  # 定义一个列表，用来存储结果
        if (os.path.exists(dcm_dir)):  # 判断路径是否存在
            files = os.listdir(dcm_dir)  # 获取该目录下的所有文件或文件夹目录
            # print(files)
            for file in files:
                m = os.path.join(dcm_dir, file)  # 得到该文件下所有目录的路径
                if (os.path.isdir(m)):  # 判断该路径下是否是文件夹
                    if 'seg' in m.lower():
                        pass
                    else:
                        h = os.path.split(m)
                        list.append(h[1])
        for pathi in list:
            niigz_filename = niigz_dir + '/images/' + pathi.split('/')[-1] + '.nii.gz'
            is_niigz = mha_validator(niigz_filename)

        if not is_niigz:
            logger.warning("niigz转换失败")
        return is_niigz, niigz_filename

    @staticmethod
    def mhd2nii(mhd_dir, nii_dir):
        mhd2nii(mhd_dir, nii_dir)

        path = os.path.join(mhd_dir, 'images')
        path = path.replace('\\', '/')
        for root, dirs, files in os.walk(path):
            for file in files:
                filename = os.path.splitext(file)[0]
                nii_filename = nii_dir + '/images/' + filename + '.nii'
            is_nii = mha_validator(nii_filename)
            print(nii_filename)
        #nii_filename = nii_dir + '/' + mhd_dir.split('/')[-1] + '.nii'
        #print(nii_filename)
        #is_nii = mhd_validator(nii_filename)

        if not is_nii:
            logger.warning("nii转换失败")
        return is_nii, nii_filename

    @staticmethod
    def mha2nii(mha_dir, nii_dir):
        mha2nii(mha_dir, nii_dir)

        path = os.path.join(mha_dir, 'images')
        path = path.replace('\\', '/')
        for root, dirs, files in os.walk(path):
            for file in files:
                filename = os.path.splitext(file)[0]
                nii_filename = nii_dir + '/images/' + filename + '.nii'
            is_nii = mha_validator(nii_filename)
            print(nii_filename)
        # nii_filename = nii_dir + '/' + mhd_dir.split('/')[-1] + '.nii'
        # print(nii_filename)
        # is_nii = mhd_validator(nii_filename)

        if not is_nii:
            logger.warning("nii转换失败")
        return is_nii, nii_filename

    @staticmethod
    def cut(data_path, save_path, format, hsize, wsize):

        segCut(data_path, save_path, format, hsize, wsize)
        is_file = os.path.isfile(save_path)
        return is_file

    @staticmethod
    def train(model_path, model_name, param_path):
        train(model_path, model_name, param_path)
        return True

    @staticmethod
    def test(model_path, model_name, param):
        test(model_path, model_name, param)
        return True
