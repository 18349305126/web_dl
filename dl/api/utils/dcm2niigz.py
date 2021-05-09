#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Class that imports and returns DICOM data via a wxPython GUI dialog."""
# Copyright (c) 2009-2017 Aditya Panchal
# Copyright (c) 2009 Roy Keyes
# This file is part of dicompyler, released under a BSD license.
#    See the file license.txt included with this distribution, also
#    available at https://github.com/bastula/dicompyler/
#
# It's assumed that the reference (prescription) dose is in cGy.

import sys
sys.path.append("../../../")

import logging
logger = logging.getLogger('dicompyler.dicomgui')
import os
import numpy as np
import cv2
from PIL import Image
import pydicom
import pydicom.uid
import pycocotools.mask as mask_util
import operator
import Levenshtein
from dicompylercore import dicomparser
from dicompylercore.dicomparser import DicomParser as dp
import shutil
import SimpleITK
#from config import Config as cfg
# from vnetloc_benchmark.config import cfg
# from vnetloc_benchmark.utils.format_api import check_structure, check_mhd
# from vnetloc_benchmark.utils.syms import mkdir
import json
import matplotlib.pyplot as pyplot

np.set_printoptions(threshold=np.inf)


def polys_to_mask(polygons, sz):
    """
    将 COCO 的多边形分割(polygon segmentation) 格式转换为数据类型为 np.float32 的 2D numpy array 的二值 mask.
    多边形分割(polygon segmentation) 被理解为在 height x width 图片中的封闭区域.
    得到的 mask shape 是 (height, width).
    """
    height, width = sz
    rle = mask_util.frPyObjects(polygons, height, width)
    mask = np.array(mask_util.decode(rle), dtype=np.float32)
    # Flatten in case polygons was a list
    mask = np.sum(mask, axis=2)
    mask = np.array(mask > 0, dtype=np.float32)
    return mask

def resize_array(arr, sz):
    im = Image.fromarray(arr)
    im = im.resize(sz)
    return np.array(im)

def DirectorySearchThread(path):
    """Search the directory."""
    patients = {}
    patients['path'] = path
    patients['series'] = {}
    # Check if the path is valid
    if os.path.isdir(path):
        files = []
        # 遍历整个目录
        for root, dirs, filenames in os.walk(path):
            files += map(lambda f:os.path.join(root, f), filenames) # 获得所有的文件
        patients['filearray'] = filenames

        # print("files:{}".format(files))

        for n in range(len(files)):
            if (os.path.isfile(files[n])):
                try:
                    logger.debug("Reading: %s", files[n])
                    dp = dicomparser.DicomParser(files[n])
                except (AttributeError, EOFError, IOError, KeyError):
                    pass
                    logger.info("%s is not a valid DICOM file.", files[n])
                else:
                    patient = dp.GetDemographics()
                    patients['demographics'] = patient
                    # Create each Series of images
                    if (('ImageOrientationPatient' in dp.ds) and \
                            not (dp.GetSOPClassUID() == 'rtdose')):
                        seinfo = dp.GetSeriesInfo()
                        seinfo['numimages'] = 0
                        seinfo['modality'] = dp.ds.SOPClassUID.name
                        if not seinfo['id'] in patients['series']:
                            patients['series'][seinfo['id']] = seinfo
                        if not 'images' in patients:
                            patients['images'] = {}
                        image = {}
                        image['id'] = dp.GetSOPInstanceUID()
                        image['filename'] = files[n]
                        image['series'] = seinfo['id']
                        image['referenceframe'] = dp.GetFrameOfReferenceUID()
                        patients['series'][seinfo['id']]['numimages'] = \
                            patients['series'][seinfo['id']]['numimages'] + 1
                        patients['images'][image['id']] = image
                    # Create each RT Structure Set
                    elif dp.ds.Modality in ['RTSTRUCT']:
                        if not 'structures' in patients:
                            patients['structures'] = {}
                        structure = dp.GetStructureInfo()
                        structure['id'] = dp.GetSOPInstanceUID()
                        structure['filename'] = files[n]
                        structure['series'] = dp.GetReferencedSeries()
                        structure['referenceframe'] = dp.GetFrameOfReferenceUID()
                        patients['structures'][structure['id']] = structure
                    # Otherwise it is a currently unsupported file
                    else:
                        logger.info("%s is a %s file and is not " + \
                            "currently supported.",
                            files[n], dp.ds.SOPClassUID.name)
        return patients
        # resultFunc(patients)
    # if the path is not valid, display an error message
    else:
        print('No dcm!')


def GetPatientData(patients):
    """Get the data of the selected patient from the DICOM importer dialog."""
    filearray = patients['filearray']
    # print(filearray)
    path = patients['path']
    # print(path)
    for n in range(0, len(filearray)):
        dcmfile = str(os.path.join(path, filearray[n]))
        dp = dicomparser.DicomParser(dcmfile)   # 解析dicom文件
        if (n == 0):
            patient = {}
        if (('ImageOrientationPatient' in dp.ds) and \
            not (dp.GetSOPClassUID() == 'rtdose')):
            if not 'images' in patient:
                patient['images'] = []
            try:
                dp.ds.file_meta.TransferSyntaxUID
            except:
                dp.ds.file_meta.TransferSyntaxUID = pydicom.uid.ImplicitVRLittleEndian
            patient['images'].append(dp.ds)
            # print(dp.ds.pixel_array.shape)
#            patient['images'][n-1].pixel_array = np.array([bytearray(patient['images'][n-1].PixelData)])\
                #.view(dtype = np.uint16).reshape(patient['images'][n-1].Rows, patient['images'][n-1].Columns)
        elif (dp.ds.Modality in ['RTSTRUCT']):
            patient['rtss'] = dp.ds
    # Sort the images based on a sort descriptor:
    # (ImagePositionPatient, InstanceNumber or AcquisitionNumber)
    if 'images' in patient:
        sortedimages = []
        unsortednums = []
        sortednums = []
        images = patient['images']
        sort = 'IPP'
        # Determine if all images in the series are parallel
        # by testing for differences in ImageOrientationPatient
        parallel = True
        for i, item in enumerate(images):
            if (i > 0):
                iop0 = np.array(item.ImageOrientationPatient)
                iop1 = np.array(images[i-1].ImageOrientationPatient)
                if (np.any(np.array(np.round(iop0 - iop1),
                dtype=np.int32))):
                    parallel = False
                    break
                # Also test ImagePositionPatient, as some series
                # use the same patient position for every slice
                ipp0 = np.array(item.ImagePositionPatient)
                ipp1 = np.array(images[i-1].ImagePositionPatient)
                if not (np.any(np.array(np.round(ipp0 - ipp1),
                dtype=np.int32))):
                    parallel = False
                    break
        # If the images are parallel, sort by ImagePositionPatient
        if parallel:
            sort = 'IPP'
        else:
            # Otherwise sort by Instance Number
            if not (images[0].InstanceNumber == \
            images[1].InstanceNumber):
                sort = 'InstanceNumber'
            # Otherwise sort by Acquisition Number
            elif not (images[0].AcquisitionNumber == \
            images[1].AcquisitionNumber):
                sort = 'AcquisitionNumber'

        # Add the sort descriptor to a list to be sorted
        for i, image in enumerate(images):
            if (sort == 'IPP'):
                unsortednums.append(image.ImagePositionPatient[2])
            else:
                unsortednums.append(image.data_element(sort).value)

        # Sort image numbers in descending order for head first patients
        if ('hf' in image.PatientPosition.lower()) and (sort == 'IPP'):
            sortednums = sorted(unsortednums, reverse=True)
        # Otherwise sort image numbers in ascending order
        else:
            sortednums = sorted(unsortednums)

        # Add the images to the array based on the sorted order
        for s, slice in enumerate(sortednums):
            for i, image in enumerate(images):
                if (sort == 'IPP'):
                    if (slice == image.ImagePositionPatient[2]):
                        sortedimages.append(image)
                elif (slice == image.data_element(sort).value):
                    sortedimages.append(image)

        # Save the images back to the patient dictionary
        patient['images'] = sortedimages
        return patient


def LoadPatientDataThread(ptdata):
    """Load the patient data."""
    patient = {}

    if not 'images' in ptdata:
        #Look for DICOM data in the ptdata dictionary
        for rtdatatype in ptdata.keys():
            if isinstance(ptdata[rtdatatype], pydicom.dataset.FileDataset):
                patient.update(dp(ptdata[rtdatatype]).GetDemographics())
                break
    if 'rtss' in ptdata:
        d = dp(ptdata['rtss'])
        s = d.GetStructures()
        for k in s.keys():
            s[k]['planes'] = d.GetStructureCoordinates(k)
            s[k]['thickness'] = d.CalculatePlaneThickness(s[k]['planes'])
        patient['structures'] = s
    if 'images' in ptdata:
        if not 'id' in patient:
            patient.update(dp(ptdata['images'][0]).GetDemographics())
        patient['images'] = []
        for image in ptdata['images']:
            patient['images'].append(dp(image))
    return patient
    # if the min/max/mean dose was not present, calculate it and save it for each structure


def DrawStructure(patient, ly, organ = 'bla'):
    for mm in patient['structures']:
        cls = check_str(patient['structures'][mm]['name'],cfg.CATEGORY, 0.5)
        if organ == cls:
            structure = patient['structures'][mm]
            break

    if not "zarray" in structure:
        structure['zarray'] = np.array(
            list(structure['planes'].keys()), dtype=np.float32)
        structure['zkeys'] = structure['planes'].keys()
    # Determine the closest z plane to the given position
    position  = '%.2f' % patient['images'][ly].GetImageData()['position'][2]
    zmin = np.amin(np.abs(structure['zarray'] - float(position)))
    index = np.argmin(np.abs(structure['zarray'] - float(position)))
    structurepixlut = patient['images'][index].GetPatientToPixelLUT()

    # Return if there are no z positions in the structure data
    if not len(structure['zarray']):
        return

    # Draw the structure only if the structure has contours
    # on the closest plane, within a threshold
    pixeldata = []
    if (zmin < 0.5):
        for contour in structure['planes'][list(structure['zkeys'])[index]]:
            if (contour['type'] == u"CLOSED_PLANAR"):
                # Convert the structure data to pixel data
                pixeldata.append(GetContourPixelData(
                    structurepixlut, contour['data']))
        return pixeldata


def GetContourPixelData(pixlut, contour, prone = False, feetfirst = False):
    """Convert structure data into pixel data using the patient to pixel LUT."""
    pixeldata = []
    # For each point in the structure data
    # look up the value in the LUT and find the corresponding pixel pair
    for p, point in enumerate(contour):
        for xv, xval in enumerate(pixlut[0]):
            if (xval > point[0] and not prone and not feetfirst):
                break
            elif (xval < point[0]):
                if feetfirst or prone:
                    break
        for yv, yval in enumerate(pixlut[1]):
            if (yval > point[1] and not prone):
                break
            elif (yval < point[1] and prone):
                break
        pixeldata.append((xv, yv))

    return pixeldata

def GetOrganStruct(ptdata, ly, organ='bla'):
    """Get structure data from images"""

    im_size = ptdata['images'][0].ds.pixel_array.shape
    stim_ = np.zeros(im_size)
    # try to convert contours into masks
    try:
        stdata_ = DrawStructure(ptdata, ly, organ)
        for stdata_i in stdata_:
            np_stdata_i = [np.array(stdata_i).reshape(len(stdata_i) * 2)]
            stim_ = stim_ + polys_to_mask(np_stdata_i, (im_size[0], im_size[1]))
    except:
        pass
    stim_ = np.array(stim_ > 0).astype(int)
    return stim_


def GetImageAndGT(path, cls, sv = False, sv_path = '.\\'):
    """Get images and groundtruth from path."""
    try:
        pts = DirectorySearchThread(path)
        pt = GetPatientData(pts)
        ptdata = LoadPatientDataThread(pt)
    except:
        print('Cannot load files in '+ path + '!')
        return None,None
    im_size = ptdata['images'][0].ds.pixel_array.shape
    ptim = np.zeros((len(ptdata['images']),)+im_size)
    stim = np.zeros((len(ptdata['images']),)+im_size)
    for ly in range(len(ptdata['images'])):
        try:
            ptim[ly] = ptdata['images'][ly].ds.pixel_array
        except:
            pti = ptdata['images'][ly].ds.pixel_array
            ptim[ly] = resize_array(pti, im_size)
        '''
        plt.subplot(121)
        plt.imshow(ptim[ly])
        stim_b = GetOrganStruct(ptdata, ly, organ='bla')
        stim_r = GetOrganStruct(ptdata, ly, organ='re')
        stim[ly] = stim_r# * 2 + stim_b
        '''
        for i, cls_i in enumerate(cls):
            if i==0:
                stim[ly] = GetOrganStruct(ptdata, ly, organ=cls_i)
            else:
                stim[ly] = stim[ly] + (i+1)*GetOrganStruct(ptdata, ly, organ=cls_i)
            stim[ly][stim[ly]>(i+1)] = i + 1
        # mm = plt.fill(np.array(stdata)[:,0],np.array(stdata)[:,1],'r')
        # aa = mm[0].xy.astype(np.int)

        '''
        plt.subplot(122)
        plt.imshow(stim[ly])
        plt.show()
        '''
        if sv:
            ptpath = pts['images'][ptdata['images'][ly].GetSOPInstanceUID()]['filename']
            path, name = os.path.split(ptpath)
            SavePatientData(ptpath, os.path.join(
                sv_path, name[:-4] + '_segmentation.DCM'), stim[ly])
    #if sv:
        #if stim.max() == 0:
            #shutil.rmtree(os.path.join(sv_path))
    return ptim, stim


def SavePatientData(filename, output_path, stim):
    """Save the data of the selected patient to the DICOM."""

    dcmfile = str(filename)
    dcm = pydicom.read_file(dcmfile, force=True)
    dcm.PixelData = stim.astype(np.uint16).tostring()
    dcm.save_as(os.path.join(output_path))


def DcmToMhd(PathDicom, SaveRawDicom, suffix, segment=False):
    lstFilesDCM = []
    # 将PathDicom文件夹下的dicom文件地址读取到lstFilesDCM中
    for dirName, subdirList, fileList in os.walk(PathDicom):
        # print(dirName)
        for filename in fileList:
            if ".dcm" in filename.lower():  # 判断文件是否为dicom文件
                if 'r' in filename.lower():
                    pass
                else:
                    lstFilesDCM.append(os.path.join(dirName, filename))  # 加入到列表中

    # print(lstFilesDCM)

    # 第一步：将第一张图片作为参考图片，并认为所有图片具有相同维度
    RefDs = pydicom.read_file(lstFilesDCM[0], force=True)  # 读取第一张dicom图片
    # image = sitk.ReadImage(lstFilesDCM[0])
    # image_array = sitk.GetArrayFromImage(image)  # z, y, x

    # 第二步：得到dicom 图片所组成3D图片的维度
    ConstPixelDims = (int(RefDs.Rows), int(RefDs.Columns), len(lstFilesDCM))  # ConstPixelDims是一个元组

    # print(ConstPixelDims)

    try:
        RefDs.file_meta.TransferSyntaxUID
    except:
        RefDs.file_meta.TransferSyntaxUID = pydicom.uid.ImplicitVRLittleEndian

    # 根据维度创建一个numpy的三维数组，并将元素类型设为：pixel_array.dtype
    ArrayDicom = np.zeros(ConstPixelDims, dtype=RefDs.pixel_array.dtype)  # array is a numpy array  dtpe=unit16
    # ArrayDicom = np.zeros(ConstPixelDims, dtype=image_array.dtype)
    # print(image_array.dtype)

    im_size = ArrayDicom.shape[:-1]     # eg(512,512)

    # 第五步:遍历所有的dicom文件，读取图像数据，存放在numpy数组中
    dses = [pydicom.read_file(filenameDCM, force=True) for filenameDCM in lstFilesDCM]
    # dses = sitk.ReadImage(lstFilesDCM)
    # ArrayDicom = sitk.GetArrayFromImage(sitk.ReadImage(lstFilesDCM))

    # print(dses)
    # print(np.array(dses[0].pixel_array).max())
    # print(np.array(dses[0].pixel_array).min())

    dses.sort(key=operator.attrgetter('InstanceNumber'),reverse=True)
    # dses = sorted(dses, key=lambda x:x.InstanceNumber)

    for i,ds in enumerate(dses):
        try:
            ds.file_meta.TransferSyntaxUID
        except:
            ds.file_meta.TransferSyntaxUID = pydicom.uid.ImplicitVRLittleEndian
        try:
            pti = ds.pixel_array
        except:
            ds.Rows, ds.Columns = im_size
            pti = ds.pixel_array
        try:
            ArrayDicom[:, :, i] = pti
        except:
            ArrayDicom[:, :, i] = resize_array(pti, im_size)


    # 第六步：对numpy数组进行转置，即把坐标轴（x,y,z）变换为（z,x,y）,这样是dicom存储文件的格式，即第一个维度为z轴便于图片堆叠
    ArrayDicom = np.transpose(ArrayDicom, (2, 0, 1))

    # 第三步：得到x方向和y方向的Spacing并得到z方向的层厚
    ConstPixelSpacing = (float(RefDs.PixelSpacing[0]), float(RefDs.PixelSpacing[1]),
                         float(round(dses[-1].ImagePositionPatient[2] - dses[0].ImagePositionPatient[2], 1)/(len(dses)-1)))
    # ConstPixelSpacing = (float(RefDs.PixelSpacing[0]), float(RefDs.PixelSpacing[1]), float(RefDs.SliceThickness))
    # thickness = dses[0].SliceThickness
    # ConstPixelSpacing = (float(thickness), float(dses[0].PixelSpacing[0]), float(dses[0].PixelSpacing[1]))
    # print(ConstPixelSpacing)

    # 第四步：得到图像的原点
    Origin = dses[0].ImagePositionPatient
    # print(Origin)

    # 第七步：将现在的numpy数组通过SimpleITK转化为mhd和raw文件
    sitk_img = sitk.GetImageFromArray(ArrayDicom, isVector=False)
    sitk_img.SetSpacing(ConstPixelSpacing)
    sitk_img.SetOrigin(Origin)
    p, d = os.path.split(dirName)
    # p, d = os.path.split(p)
    if segment:
        sv_dir = os.path.join(SaveRawDicom, "labels")
        mkdir(sv_dir)
        sv_path = os.path.join(sv_dir, d + "_segmentation" + suffix)
    else:
        sv_dir = os.path.join(SaveRawDicom, "images")
        mkdir(sv_dir)
        sv_path = os.path.join(sv_dir, d + suffix)
    SimpleITK.WriteImage(sitk_img, sv_path)


# path: the path of dcm
# sv_path: the path of segment
# sv_raw_path: the path of mhd
def transAll(path, sv_path, sv_raw_path, category, suffix):
    cls = category
    path=path.replace('\\', '/')
    sv_path = sv_path.replace('\\', '/')
    sv_raw_path = sv_raw_path.replace('\\', '/')
    #path = 'Z:\MRI\data\T1seg'
    mkdir(os.path.join(sv_path))
    print(path + ' is being converted to'+ suffix + '!')
    im, gt = GetImageAndGT(path, cls, True, sv_path)
    if os.path.isdir(os.path.join(sv_path)):
        mkdir(os.path.join(sv_raw_path))
        DcmToMhd(path, sv_raw_path,suffix)
        DcmToMhd(sv_path, sv_raw_path, suffix, segment=True)
        print(path + ' has been converted to'+ suffix + '!')

def DirList(path):
    list = []  # 定义一个列表，用来存储结果
    if (os.path.exists(path)):  # 判断路径是否存在
        files = os.listdir(path)  # 获取该目录下的所有文件或文件夹目录
        # print(files)
        for file in files:
            m = os.path.join(path, file)  # 得到该文件下所有目录的路径
            if (os.path.isdir(m)):  # 判断该路径下是否是文件夹
                if 'seg' in m.lower():
                    pass
                else:
                    h = os.path.split(m)
                    list.append(h[1])
    return list

# 校正正确的器官名称（输入：b->获得的名称；a->正确的名称列表；输出：b的正确名称）
def check_str(b, a, alpha = 0.7):
    a_s = [Levenshtein.ratio(a_i.lower(), b.lower()) for a_i in a]
    a_l = [Levenshtein.ratio(a_i, b) for a_i in a]
    # if max(max(cls_s))<0.8:
    # dcm_str_cls.ROIName = cls_all[cls_s.index(max(cls_s))]
    s_ind, l_ind = a_s.index(max(a_s)), a_l.index(max(a_l))
    if max(a_s[s_ind], a_l[l_ind]) > alpha:
        ind = s_ind
        if s_ind != l_ind:
            if a_s[s_ind] + a_l[s_ind] > a_s[l_ind] + a_l[l_ind]:
                ind = s_ind
        return a[ind]

    return ''


class CheckPoint(object):
    def __init__(self, dir='./', mhd_list=None):
        if mhd_list==None:
            self.mhd_dict={}
        else:
            self.mhd_dict = mhd_list
        self.dir = dir
        self.load_point()

    def save_point(self):
        json_str = json.dumps(self.mhd_dict, indent=2)
        save_file = os.path.join(self.dir, "check_point.json")
        with open(save_file, "w") as f:
            f.write(str(json_str))

    def check_mhd(self, mhd):
        return check_dict(mhd, self.mhd_dict.copy())

    def load_point(self):
        save_file = os.path.join(self.dir, "check_point.json")
        try:
            with open(save_file, "r") as f:
                self.mhd_dict = json.load(f)
        except IOError:
            # if file doesn't exist, maybe because it has just been
            # deleted by a separate process
            self.mhd_dict = {}

def check_dict(b, a):
    b_in_a = True
    for b_k_i in b.keys():
        for b_i_k in b[b_k_i].keys():
            if b_k_i in a.keys():
                if b_i_k in a[b_k_i].keys():
                    for b_i_i in b[b_k_i][b_i_k]:
                        if b_i_i not in a[b_k_i][b_i_k]:
                            a[b_k_i][b_i_k].append(b_i_i)
                            b_in_a = False
                else:
                    b_in_a = False
                    a[b_k_i].update(b[b_k_i])
            else:
                b_in_a = False
                a.update(b)
    return a, b_in_a

def getSequence(file_path):
    pathss = []
    for root, dirs, files in os.walk(file_path):
        path = [os.path.join(root,name) for name in files]
        pathss.extend(path)
    pathv = [pathd.split('/')[-2] for pathd in pathss]
    pathv = set(pathv)
    pathv = list(pathv)
    # print(pathv)
    return pathv

def dcm2niigz(dcm_dir, nii_dir, seg_path,category):
    suffix = '.nii.gz'
    path_all = dcm_dir
    # print(path_all)
    save_all = nii_dir
    seq_cls = getSequence(path_all)
    seg_path = seg_path
    dir_list = DirList(path_all)
    chp = CheckPoint(path_all)
    # print(dir_list)


    for pathi in dir_list:
        print(pathi)
        path = os.path.join(path_all, pathi)
        # sv_path = os.path.join(seg_path,  pathi + '_segmentation')
        sv_path = os.path.join(seg_path,  pathi)
        sv_raw_path = os.path.join(save_all, check_str(pathi, seq_cls, 0))
        # sv_raw_path = os.path.join(save_all, dir_dt, pathi)
        # mhd_list, ext = chp.check_mhd(pathi)
        transAll(path, sv_path, sv_raw_path, category, suffix)


def mkdir(path):
    path = path.strip() # 去除空格
    path = path.rstrip("\\")# 去除尾部 \ 符号
    isExists = os.path.exists(path) # 判断路径是否存在
    if not isExists:
        os.makedirs(path)# 如果不存在则创建目录
        return True
    else:
        return False # 如果目录存在则不创建

def getSequenceName(path):
    series_IDs = SimpleITK.ImageSeriesReader.GetGDCMSeriesIDs(path)
    nb_series = len(series_IDs)  # 查看该文件夹下的序列数量
    series_file_names = SimpleITK.ImageSeriesReader.GetGDCMSeriesFileNames(path, series_IDs[1])
    series_names = [names.split('/')[-1] for names in series_file_names]
    return series_names

def ImageToMatrix(filename):
    # 读取图片
    im = Image.open(filename)
    # 显示图片
#     im.show()
    width,height = im.size
    im = im.convert("L")
    data = im.getdata()
    data = np.matrix(data,dtype='float')
    #new_data = np.reshape(data,(width,height))
    new_data = np.reshape(data,(height,width))
    return new_data
#     new_im = Image.fromarray(new_data)
#     # 显示图片
#     new_im.show()


import SimpleITK as sitk
if __name__ == "__main__":
    dcm2niigz()
