import numpy as np
import os
import cv2
import SimpleITK as sitk
from scipy.misc import imsave


# 将数据文件里面的数组读取出来
def load_data_volume_as_array(filename):
    img = sitk.ReadImage(filename)
    nda = sitk.GetArrayFromImage(img)
    return nda


def segCut(data_path, save_path, format, hsize, wsize):
    file = os.listdir(data_path)
    # num = len(file)
    #fname = os.listdir(os.path.join(data_path, file[0]))
    fname = file[0]


    # 判断数据的类型
    types = ''
    fn = fname
    print(fn)
    if '.mhd' in fn:
        types = '.mhd'
    if '.mha' in fn:
        types = '.mha'
    if '.nii.gz' in fn:
        types = '.nii.gz'
    elif '.nii' in fn:
        types = '.nii'


    for filename in file:
        print(filename)

        #r_nda3D = load_data_volume_as_array(os.path.join(data_path, filename) + '/'+filename + types)  # 获取每个病例的3D数组
        #s_nda3D = load_data_volume_as_array(os.path.join(data_path, filename) + '/'+filename + '_segmentation_segmentation' + types)
        r_nda3D = load_data_volume_as_array(os.path.join(data_path, filename))  # 获取每个病例的3D数组
        s_nda3D = load_data_volume_as_array(os.path.join(data_path, filename))

        t = np.nonzero(s_nda3D)
        x1 = np.max(t[0])
        y1 = np.max(t[1])
        z1 = np.max(t[2])
        x2 = np.min(t[0])
        y2 = np.min(t[1])
        z2 = np.min(t[2])
        # print("({}_{},{}_{},{}_{})".format(x2, x1, y2, y1, z2, z1))

        if (x1 - x2 + 1 > hsize) or (y2-1):
            s_nda3D = s_nda3D[np.ix_(range(x2, x1 + 1), range(y2, y1 + 1), range(z2, z1 + 1))]  # 切取器官所在区域
            r_nda3D = r_nda3D[np.ix_(range(x2, x1 + 1), range(y2, y1 + 1), range(z2, z1 + 1))]
            n = x1 - x2 + 1
            x = []
            y = []
            for j in range(n):
                s_nda3D_new = cv2.resize(s_nda3D[j], (hsize, wsize))  # 获取每张切片的2D数组
                r_nda3D_new = cv2.resize(r_nda3D[j], (hsize, wsize))
                x.append(r_nda3D_new)
                y.append(s_nda3D_new)
            s_nda3D = np.asarray(y)
            r_nda3D = np.asarray(x)
        else:

            s_nda3D = s_nda3D[np.ix_(range(x2, x1 + 1), range(int((y2 + y1 - hsize)/2), int((y2 + y1 + hsize)/2)),
                                     range(int((z2 + z1 - wsize)/2), int((z2 + z1 + wsize)/2)))]  # 切取器官所在区域
            r_nda3D = r_nda3D[np.ix_(range(x2, x1 + 1), range(int((y2 + y1 - hsize)/2), int((y2 + y1 + hsize)/2)),
                                     range(int((z2 + z1 - wsize)/2), int((z2 + z1 + wsize)/2)))]

        if format == '3D':
            filename = os.path.splitext(filename)[0]
            sitk_img = sitk.GetImageFromArray(r_nda3D, isVector=False)
            sitk.WriteImage(sitk_img, os.path.join(save_path + '/images', filename + '.nii'))
            sitk_lab = sitk.GetImageFromArray(s_nda3D, isVector=False)
            sitk.WriteImage(sitk_lab, os.path.join(save_path + '/labels', filename + '_mask.nii'))

        if format == '2D':
            filename = os.path.splitext(filename)[0]
            for nums in range(r_nda3D.shape[0]):
                #imsave(os.path.join(save_path+'/images', filename + '_' + str(nums) + '.png'), r_nda3D[nums])
                #np.save(os.path.join(save_path+'/labels', filename + '_'+ str(nums) + '_mask.npy'), s_nda3D[nums])
                imsave(os.path.join(save_path+'/images', filename + '_' + str(nums) + '.png'), r_nda3D[nums])
                np.save(os.path.join(save_path+'/labels', filename + '_'+ str(nums) + '_mask.npy'), s_nda3D[nums])

        print('The data of patient {} have been cut!'.format(filename))


if __name__ == '__main__':
    #data_path = 'F:\Contouring\Data\\test\\nii\SY'
    data_path = 'E:/university/dasishang/bishe/code/WebDL-master10/WebDL-master/dl/api/utils/data/mhd/test/images'
    save_path = 'E:/university/dasishang/bishe/code/WebDL-master10/WebDL-master/data/test/cut'
    #data_path = 'E:\university\dasishang\bishe\code\数据样例\0_nii\'
    #save_path = 'E:\university\dasishang\bishe\code\WebDL-master10\WebDL-master\data\test'
    format = '2D'
    hsize = 256
    wsize = 256
    segCut(data_path, save_path, format, hsize, wsize)