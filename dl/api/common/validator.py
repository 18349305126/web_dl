import os
import SimpleITK as sitk
from api.common.logger import logger


def mhd_validator(filename):
    if not os.path.exists(filename):
        return False
    try:
        img = sitk.ReadImage(filename)
        nda = sitk.GetArrayFromImage(img)
    except RuntimeError:
        logger.error('Not image file')
        return False

    return True

def mha_validator(filename):
    if not os.path.exists(filename):
        return False
    try:
        img = sitk.ReadImage(filename)
        nda = sitk.GetArrayFromImage(img)
    except RuntimeError:
        logger.error('Not image file')
        return False

    return True