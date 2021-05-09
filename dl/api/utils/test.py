import numpy as np
import os
from api.utils import LoadData
from api.utils import tools


def test(model_path, model_name,param):
    import sys
    sys.path.append(model_path)
    import importlib
    Net = importlib.import_module(model_name)  # 绝对导入
    #import UNet
    from api.utils.config import Config as cfg

    my_model = getattr(Net, model_name)

    os.environ["CUDA_VISIBLE_DEVICES"] = "3"

    n_classes = 6
    input_height = 256
    input_width = 256

    path1 = os.path.join(cfg.MHD_DIR, 'test/images/')
    path2 = os.path.join(cfg.MHD_DIR, 'test/labels')

    X_test, y_test = LoadData.data_generator_xd(path1, path2)
    # X_test, y_test = dataGenerator.test_generator_xd(path, input_height, input_width)

    X_test = np.expand_dims(X_test, axis=-1)
    # y_test = np.expand_dims(y_test, axis=-1)
    # y_test = tools.one_hot(y_test, n_classes)
    print(X_test.shape)
    print(y_test.shape)

    m = my_model(n_classes, input_height, input_width)  # 有自定义层时，不能直接加载模型
    #m = method[key](n_classes, input_height, input_width)  # 有自定义层时，不能直接加载模型
    m.load_weights(param.format(model_name))
    # m.load_weights('checkpoints/fcn32_model_256.hdf5'.format(key))

    y_pred = m.predict(X_test, batch_size=1, verbose=1)
    # max_index = np.argmax(y_pred, axis=-1)
    # for i in range(y_pred.shape[0]):
    #     for j in range(y_pred.shape[1]):
    #         y_pred[i][j] = 0
    #         y_pred[i][j][max_index[i, j]] = 1

    # print(y_pred)
    # y_pred = preprocessing.MinMaxScaler().fit_transform(y_pred)
    # print(y_pred)

    y_pred = tools.softmax_to_one_hot(y_pred, depth=n_classes)
    image = [np.argmax(one_hot, axis=-1) for one_hot in y_pred]
    image = np.array(image).reshape(y_pred.shape[0], input_height, input_width)

    # 计算总体的dice
    dice = tools.dice_coef(y_test, image)
    loss = 1. - dice
    print('dice: {}'.format(dice))
    print('loss: {}'.format(loss))

    # 单独计算每个器官的dice
    dices = tools.dice(y_test, image, 6)
    print('dices: {}'.format(dices))

    # 保存分割结果
    # for k in range(y_pred.shape[0]):
    #     scipy.misc.imsave('image/%s.jpg' % k, y_pred[k])
    # print("Finish!!!")
    # # np.save('\\results\\imgs_mask_test.npy',y_pred)

if __name__ == "__main__":
    model_path = "E:/university/dasishang/bishe/code/导入模型并测试/code/Models"
    model_name = 'UNet'
    param = 'E:/university/dasishang/bishe/code/导入模型并测试/code/unet_model_32.hdf5'
    test(model_path, model_name, param)