# -*- coding: utf-8 -*-

import tensorflow as tf
import numpy as np
import os
from keras.optimizers import Adam
from api.utils import LoadData
from api.utils import tools
from keras.callbacks import EarlyStopping, ReduceLROnPlateau, ModelCheckpoint, TensorBoard
from sklearn.model_selection import train_test_split

from keras.backend.tensorflow_backend import set_session

from keras.preprocessing.image import ImageDataGenerator


def train(model_path, model_name, param_path):
    import sys
    sys.path.append(model_path)
    import importlib
    Net = importlib.import_module(model_name)  # 绝对导入
    # import UNet
    from api.utils.config import Config as cfg

    my_model = getattr(Net, model_name)
    # os.environ["CUDA_VISIBLE_DEVICES"] = "3"
    config = tf.ConfigProto(allow_soft_placement=True, log_device_placement=True)
    config.gpu_options.allow_growth = True
    set_session(tf.Session(config=config))

    sess = tf.Session()
    sess.run(tf.global_variables_initializer())

    path1 = os.path.join(cfg.MHD_DIR, 'train/images')
    path2 = os.path.join(cfg.MHD_DIR, 'train/labels')
    path1 = path1.replace('\\', '/')
    path2 = path2.replace('\\', '/')

    n_classes = 6
    input_height = 256
    input_width = 256
    batch_size = 2
    epochs = 1000
    key = model_name


    x, y = LoadData.data_generator_xd(path1, path2)

    x = np.expand_dims(x, axis=-1)
    # y = np.expand_dims(y, axis=-1)
    y = tools.one_hot(y, n_classes)
    # y = y.reshape((-1,input_height * input_width,6))

    X_train, X_valid, y_train, y_valid = train_test_split(x, y, test_size=0.3)

    print('y_train.shape: {}'.format(y_train.shape))
    print('X_valid.shape: {}'.format(X_valid.shape))

    print('y_train.shape: {}'.format(y_train.shape))
    print('y_valid.shape: {}'.format(y_valid.shape))

    # input_img = Input(shape=(input_height,input_width,1))
    # m = Conv2D(3, (1, 1), strides=1, activation='relu')(input_img)
    m = my_model(n_classes, input_height=input_height, input_width=input_width)
    # m.load_weights('checkpoints/{}_model.hdf5'.format(key))
    m.compile(loss='categorical_crossentropy',
              optimizer=Adam(lr=1.0e-4),
              metrics=[tools.k_dice_coef])

    img = ImageDataGenerator(
        featurewise_center=False,
        samplewise_center=False,
        featurewise_std_normalization=False,
        samplewise_std_normalization=False,
        zca_whitening=False,
        rotation_range=0.2,
        width_shift_range=0.2,
        height_shift_range=0.2,
        shear_range=0.2,
        zoom_range=0.2,
        channel_shift_range=0.,
        fill_mode='nearest',
        cval=0.0,
        horizontal_flip=False,
        vertical_flip=False,
        rescale=None,
        preprocessing_function=None,
        data_format="channels_last")

    filepath = os.path.join(param_path, '%s_model.hdf5' % key)
    filepath = filepath.replace('\\', '/')
    print(filepath)


    callbacks = [
        ReduceLROnPlateau(monitor='loss', factor=0.5, patience=3, mode='min',
                          min_delta=0.005, cooldown=1, verbose=1, min_lr=1e-10),
        TensorBoard(),
        EarlyStopping(monitor='loss', min_delta=0.001, mode='min',
                      verbose=1, patience=10),
        ModelCheckpoint(
            filepath,
            verbose=True,
            save_best_only=True,
            monitor='loss',
            mode='min')
    ]
    hists = []

    hist = m.fit_generator(
        img.flow(X_train, y_train, batch_size=batch_size),
        validation_data=(X_valid, y_valid),
        steps_per_epoch=len(X_train) // batch_size,
        epochs=epochs,
        validation_steps=100,
        callbacks=callbacks
    )

    hists.append(hist)

if __name__ == "__main__":
    model_path = "D:/lyh/code/bishe/WebDL-master07/WebDL-master/dl/api/utils/Models"
    model_name = 'UNet'
    param_path = 'D:/lyh/code/bishe/WebDL-master07/WebDL-master/dl/api/utils/checkpoints'
    train(model_path, model_name, param_path)
