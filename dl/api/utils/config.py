#!/usr/bin/env python
# -*- coding: utf-8 -*- #

import SimpleITK as sitk
import os

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

class Config(object):
    DICOM_DIR = "D:/lyh/code/bishe/WebDL-master11/WebDL-master/data/dcm"
    #    NII_DIR = "../Data/MHD"
    SEQUENCE = getSequence(DICOM_DIR)
    SEGMENTAION_PATH = "D:/lyh/code/bishe/WebDL-master11/WebDL-master/data/test/segment"
    MHD_DIR = "D:/lyh/code/bishe/WebDL-master11/WebDL-master/data/mhd"
    NII_DIR = "D:/lyh/code/bishe/WebDL-master11/WebDL-master/data/test/nii"
    MHA_DIR = 'D:/lyh/code/bishe/WebDL-master11/WebDL-master/data/test/mha'
    CATEGORY = ['Parotid_R', 'Parotid_L', 'Submandibular_L', 'Sunmandibular_R', 'OralCavity']

    def __init__(self):
        self = self.__init__()



