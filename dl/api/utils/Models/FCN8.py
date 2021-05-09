from keras.applications import vgg16
from keras.models import Model, Sequential
from keras.layers import Conv2D, Conv2DTranspose, Input, Cropping2D, add, Dropout, Reshape, Activation


def FCN8_helper(nClasses, input_height, input_width):

    assert input_height % 32 == 0
    assert input_width % 32 == 0

    img_input = Input(shape=(input_height, input_width, 1))
    ft = Conv2D(filters=3, kernel_size=3, padding='same',
                  kernel_initializer='glorot_normal', bias_initializer='zeros')(img_input)
    md = Model(inputs=img_input, outputs=ft)

    # # [batch_size, height, width,  1] -> [batch_size, heigth, width, 3]
    # img_input = tf.image.grayscale_to_rgb(img_input)
    # print('img_input : {}'.format(img_input.get_shape()))
    model = vgg16.VGG16(
        include_top=False,  # 不包括顶层的全连接层
        weights=None,  # 加载在 ImageNet 上预训练的权值
        input_tensor=md.output,
        pooling=None,  # 不池化
        classes=1000)
    assert isinstance(model, Model) # 判断model是Model类型的

    o = Conv2D(filters=4096, kernel_size=(7, 7), padding="same", activation="relu", name="fc6")(model.output)
    o = Dropout(rate=0.5)(o)
    o = Conv2D(filters=4096, kernel_size=(1, 1), padding="same", activation="relu", name="fc7")(o)
    o = Dropout(rate=0.5)(o)
    o = Conv2D(filters=nClasses, kernel_size=(1, 1), padding="same", activation="relu", kernel_initializer="he_normal",name="score_fr")(o)
    o = Conv2DTranspose(filters=nClasses, kernel_size=(2, 2), strides=(2, 2), padding="valid", activation=None,name="score2")(o)

    fcn8 = Model(inputs=img_input, outputs=o)
    # fcn8.summary()
    return fcn8


def FCN8(nClasses, input_height, input_width):

    fcn8 = FCN8_helper(nClasses, input_height, input_width)

    # Conv to be applied on Pool4
    skip_con1 = Conv2D(nClasses, kernel_size=(1, 1), padding="same", activation=None, kernel_initializer="he_normal",
                       name="score_pool4")(fcn8.get_layer("block4_pool").output)

    # print('block4_pool shape: {}'.format(fcn8.get_layer("block4_pool").output.get_shape()))

    Summed = add(inputs=[skip_con1, fcn8.output])
    # print(Summed.get_shape())
    x = Conv2DTranspose(nClasses, kernel_size=(2, 2), strides=(2, 2), padding="valid", activation=None,
                        name="score4")(Summed)
    # print(x.get_shape())
    ###
    skip_con2 = Conv2D(nClasses, kernel_size=(1, 1), padding="same", activation=None, kernel_initializer="he_normal",
                       name="score_pool3")(fcn8.get_layer("block3_pool").output)
    Summed2 = add(inputs=[skip_con2, x])
    # print(Summed2.get_shape())
    #####
    Up = Conv2DTranspose(nClasses, kernel_size=(8, 8), strides=(8, 8),
                         padding="valid", activation=None, name="upsample")(Summed2)

    # print('Up shape: {}'.format(Up.get_shape()))

    # # print(Up.get_shape())
    # Up = Reshape((-1, nClasses))(Up)
    # print(Up.get_shape())
    Up = Activation("softmax")(Up)

    mymodel = Model(inputs=fcn8.input, outputs=Up)

    return mymodel


# if __name__ == '__main__':
#     m = FCN8(6, 512, 512)
#     # from keras.utils import plot_model
#     # plot_model(m, show_shapes=True, to_file='model_fcn8_1.png')
#     print(len(m.layers))
