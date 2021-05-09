import SimpleITK as sitk
import numpy as np
import pydicom
import pandas as pd
import operator
import os
import cv2

# os.environ["CUDA_VISIBLE_DEVICES"] = "1"


def getDCMlist(PathDicom):
    lstFilesDCM = []
    RSPath = ''
    # 将PathDicom文件夹下的dicom文件地址读取到lstFilesDCM中
    for dirName, subdirList, fileList in os.walk(PathDicom):
    # for fileList in os.listdir(PathDicom):
        for filename in fileList:
            if ".dcm" in filename:  # 判断文件是否为dicom文件
                if 'RS' in filename:
                    # RSPath.append(os.path.join(dirName, filename))
                    RSPath = os.path.join(dirName, filename)
                    # print(RSPath)
#                elif 'RD.' or 'RP.' in filename:
#                    pass
                else:
                    lstFilesDCM.append(os.path.join(dirName, filename))  # 加入到列表中

    return lstFilesDCM, RSPath


def dictOfROI(RSpath):
    RSInfo = pydicom.read_file(RSpath, force=True)
    RSInfoROISeq = RSInfo.StructureSetROISequence

    d = dict()
    for i in RSInfo.StructureSetROISequence:
        d[i.ROIName] = i.ROINumber
    return d


def pdOfUidAROI(RSpath, testROI):
    RSInfo = pydicom.read_file(RSpath, force=True)
    RSInfoConSeq = RSInfo.ROIContourSequence
    dictofROI = dictOfROI(RSpath)
    print(dictOfROI)

    testROINumber = [] 
    for i in testROI:
        testROINumber.append(dictofROI[i])
    
    testROIOfUid = dict()
    for i in RSInfoConSeq:
        if i.ReferencedROINumber in testROINumber:
            testROIOfUid[i.ReferencedROINumber] = []
            for j in i.ContourSequence:
                for k in j.ContourImageSequence:
                    testROIOfUid[i.ReferencedROINumber].append(k.ReferencedSOPInstanceUID)

    # 根据ct的id去掉重复的ct
    ctUidTmp = []
    for i in testROIOfUid.keys():
        uid = testROIOfUid[i]
        for j in uid:
            ctUidTmp.append(j)
    ctUid = []
    [ctUid.append(i) for i in ctUidTmp if i not in ctUid]

    ROIOfUid = pd.DataFrame(index=ctUid, columns=testROIOfUid.keys())
    for i in testROIOfUid.keys():
        for j in ROIOfUid.index:
            if j in testROIOfUid[i]:
                ROIOfUid.loc[j, i] = True
            else:
                ROIOfUid.loc[j, i] = False
    ROIOfUid.sort_index(inplace=True)
    return ROIOfUid


def drawCTAndROI(PathDicom, testROI,  testID):
    dcmlist, RSpath = getDCMlist(PathDicom)
#    print(dcmlist)

    pdUidAndRoi = pdOfUidAROI(RSpath, testROI)
    dictROINum = dictOfROI(RSpath)
    # print(dictROINum.values())
    RSInfo = pydicom.read_file(RSpath, force=True)
    DcmInfo = pydicom.read_file(dcmlist[0], force=True)
    # ConstPixelDims = (int(DcmInfo.Rows), int(DcmInfo.Columns), len(dcmlist))

    dcms = [pydicom.read_file(filenameDCM, force=True) for filenameDCM in dcmlist]
    dcms.sort(key=operator.attrgetter('InstanceNumber'), reverse=True)
    ctUids = [dcmInfo.SOPInstanceUID for dcmInfo in dcms]

    images = []
    labels = []
    spacing = []
    position =[]

    for n, i in enumerate(ctUids):
        ctInfo = pydicom.read_file(os.path.join(PathDicom, 'CT.' + i + '.dcm'), force=True)
        ctInfo.file_meta.TransferSyntaxUID = pydicom.uid.ImplicitVRLittleEndian  # or whatever is the correct transfer syntax for the file
        imgPos = ctInfo.ImagePositionPatient
        imgSpacing = ctInfo.PixelSpacing
        img = ctInfo.pixel_array
        images.append(img)

        if n == 1 or n == 2:
            position.append(imgPos)
            spacing.append(imgSpacing)

        mrPoint = np.zeros(img.shape, np.uint16)

        if i in (pdUidAndRoi.index):
            for thOra, j in enumerate(pdUidAndRoi.columns):
                if pdUidAndRoi.loc[i, j]:
                    for k in RSInfo.ROIContourSequence:
                        if k.ReferencedROINumber == j:
                            numOfContour = None
                            contourData = None
                            for ii in k.ContourSequence:
                                for jj in ii.ContourImageSequence:
                                    if jj.ReferencedSOPInstanceUID == i:
                                        numOfContour = ii.NumberOfContourPoints
                                        contourData = ii.ContourData

                            contourDataTrans = np.zeros((numOfContour, 3))
                            contourDataReal = np.zeros((numOfContour, 2))
                            for ii in range(numOfContour):
                                contourDataTrans[ii, 0] = contourData[ii * 3]
                                contourDataTrans[ii, 1] = contourData[ii * 3 + 1]
                                contourDataTrans[ii, 2] = contourData[ii * 3 + 2]
                            for ii in range(numOfContour):
                                contourDataReal[ii, 0] = round((contourDataTrans[ii, 0] - imgPos[0]) / imgSpacing[0])
                                contourDataReal[ii, 1] = round((contourDataTrans[ii, 1] - imgPos[1]) / imgSpacing[1])
                            contourDataReal = contourDataReal.reshape((-1, 1, contourDataReal.shape[1]))

                            x = np.arange(0, 513)
                            y = np.arange(0, 513)
                            xx, yy = np.meshgrid(x, y)

                            for xi in range(xx.shape[0]):
                                for xj in range(xx.shape[1]):

                                    mask = cv2.pointPolygonTest(np.int32(contourDataReal), (xx[xi, xj], yy[xi, xj]), False)
                                    if (mask == 0) or (mask > 0):
                                        roiName = list(dictROINum.keys())[list(dictROINum.values()).index(j)]
                                        roiIndex = testROI.index(roiName)
                                        roiID = testID[roiIndex]
                                        # print("name:{},ID:{}".format(roiName, roiID))
                                        mrPoint[xi, xj] = roiID

        labels.append(mrPoint)
        # print("load {} dcm!".format(n))

    ConstPixelSpacing = (float(spacing[0][0]), float(spacing[0][1]), float(round(position[1][2] - position[0][2], 1)))
    origin = position[0]
    # print(ConstPixelSpacing)
    # print(origin)
    return np.array(images), np.array(labels), ConstPixelSpacing, origin


def main(path, savepath):
#    pathlist = os.listdir(path)
    testROI = ['Parotid_L', 'Parotid_R', 'Submandibula_L', 'Sunmandibula_R', 'OralCavity']
    testID = [1, 2, 3, 4, 5]
    PathDicom = path
    getDCMlist(PathDicom)
    images, labels, ConstPixelSpacing, Origin = drawCTAndROI(PathDicom, testROI, testID)
    sitk_img = sitk.GetImageFromArray(images, isVector=False)
    sitk_lab = sitk.GetImageFromArray(labels, isVector=False)
    sitk_img.SetSpacing(ConstPixelSpacing)
    sitk_img.SetOrigin(Origin)
    d = os.path.split(PathDicom)[-1]
    img_path = os.path.join(savepath, 'images')
    if not os.path.exists(img_path):
        os.mkdir(img_path)
    lab_path = os.path.join(savepath, 'labels')
    if not os.path.exists(lab_path):
        os.mkdir(lab_path)
    # 存储格式可为 mhd mha nii nii.gz 
    #sv_ipath = os.path.join(img_path, d + ".mhd")
    #sv_lpath = os.path.join(lab_path, d + "_segmentation" + ".mhd")
    sv_ipath = os.path.join(img_path, d + ".mha")
    sv_lpath = os.path.join(lab_path, d + "_segmentation" + ".mha")
    sitk.WriteImage(sitk_img, sv_ipath)
    sitk.WriteImage(sitk_lab, sv_lpath)



if __name__ == "__main__":
    path = './data/dcm/00C1193200'
    #savepath = './data/mhd/train'
    savepath = './data/mha/train'
    main(path, savepath)
