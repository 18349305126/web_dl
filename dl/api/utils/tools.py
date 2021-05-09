# -*- coding: utf-8 -*-

import tensorflow as tf
import numpy as np
from keras import backend as K
import SimpleITK as sitk


def one_hot(nparray, depth=0, on_value=1, off_value=0):
    if depth == 0:
        depth = np.max(nparray) + 1
    assert np.max(nparray) < depth, "the max index of nparray: {} is larger than depth: {}".format(np.max(nparray), depth)
    shape = nparray.shape
    out = np.ones((*shape, depth)) * off_value
    indices = []
    for i in range(nparray.ndim):
        tiles = [1] * nparray.ndim
        s = [1] * nparray.ndim
        s[i] = -1
        r = np.arange(shape[i]).reshape(s)
        if i > 0:
            tiles[i-1] = shape[i-1]
            r = np.tile(r, tiles)
        indices.append(r)
    indices.append(nparray)
    out[tuple(indices)] = on_value
    return out


# dice系数
def k_dice_coef(y_true, y_pred):
    smooth = 1.
    y_true_f = K.flatten(y_true)
    y_pred_f = K.flatten(y_pred)
    intersection = K.sum(y_true_f * y_pred_f)
    return (2. * intersection + smooth) / (K.sum(y_true_f) + K.sum(y_pred_f) + smooth)
    # return (2. * intersection + smooth) / (K.sum(y_true_f * y_true_f) + K.sum(y_pred_f * y_pred_f) + smooth)


# def k_dice_coef(y_true, y_pred):
#     return tf.py_func(dice_coef, [y_true, y_pred], Tout=[tf.float64])


def dice_coef(lT, lP):
    labelPred = sitk.GetImageFromArray(lP, isVector=False)
    labelTrue = sitk.GetImageFromArray(lT, isVector=False)
    dicecomputer = sitk.LabelOverlapMeasuresImageFilter()
    dicecomputer.Execute(labelTrue > 0.5, labelPred > 0.5)
    dice = dicecomputer.GetDiceCoefficient()
    return dice


# def dice_coef(y_true, y_pred, smooth=1):
#     intersection = K.sum(y_true * y_pred, axis=1)
#     union = K.sum(y_true, axis=1) + K.sum(y_pred, axis=1)
#     dice = K.mean((2. * intersection + smooth) / (union + smooth), axis=0)
#     return dice


# dice系数损失函数
def dice_coef_loss(y_true, y_pred):
    return 1 - k_dice_coef(y_true, y_pred)


def softmax_to_one_hot(tensor, depth):
    max_idx = np.argmax(tensor, axis=-1)
    tensor_one_hot = one_hot(max_idx, depth=depth)
    return tensor_one_hot


# 计算每个器官的dice
def dice(predictions, labels, num_classes):
    """Calculates the categorical Dice similarity coefficients for each class
        between labels and predictions.

    Args:
        predictions (np.ndarray): predictions
        labels (np.ndarray): labels
        num_classes (int): number of classes to calculate the dice
            coefficient for

    Returns:
        np.ndarray: dice coefficient per class or NaN if class not present
    """

    dice_scores = np.zeros((num_classes))

    for i in range(num_classes):
        tmp_den = (np.sum(predictions == i) + np.sum(labels == i))
        tmp_dice = 2. * np.sum((predictions == i) * (labels == i)) / tmp_den
        dice_scores[i] = tmp_dice
    print("dices_compute:{}".format(dice_scores))
    return dice_scores.astype(np.float32)

