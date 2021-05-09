from keras.applications import vgg16
from keras.models import Model, Sequential
from keras.layers import Conv2D, Conv2DTranspose, Input, Cropping2D, add, Dropout, Reshape, Activation
from keras.utils import plot_model


def FCN32(nClasses, input_height, input_width):

    assert input_height % 32 == 0
    assert input_width % 32 == 0

    img_input = Input(shape=(input_height, input_width, 1))
    ft = Conv2D(filters=3, kernel_size=3, padding='same',
                  kernel_initializer='glorot_normal', bias_initializer='zeros')(img_input)
    md = Model(inputs=img_input, outputs=ft)

    model = vgg16.VGG16(
        include_top=False,
        weights=None,
        input_tensor=md.output)
    assert isinstance(model, Model)

    o = Conv2D(filters=4096, kernel_size=(7, 7), padding="same", activation="relu", name="fc6")(model.output)
    o = Dropout(rate=0.5)(o)
    o = Conv2D(filters=4096, kernel_size=(1, 1), padding="same", activation="relu", name="fc7")(o)
    o = Dropout(rate=0.5)(o)
    o = Conv2D(filters=nClasses, kernel_size=(1, 1), padding="same", activation="relu",
               kernel_initializer="he_normal", name="score_fr")(o)
    o = Conv2DTranspose(filters=nClasses, kernel_size=(32, 32), strides=(32, 32), padding="valid",
                        activation=None, name="score2")(o)

    # o = Reshape((-1, nClasses))(o)
    o = Activation("softmax")(o)

    fcn32 = Model(inputs=img_input, outputs=o)
    # mymodel.summary()
    return fcn32


# if __name__ == '__main__':
#     m = FCN32(15, 320, 320)
#     m.summary()
#     plot_model(m, show_shapes=True, to_file='model_fcn32.png')
#     print(len(m.layers))
