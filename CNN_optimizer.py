from tensorflow.python.keras.models import Sequential
from tensorflow.python.keras.layers import Conv2D, MaxPooling2D
from tensorflow.python.keras.layers import Activation, Dropout, Flatten, Dense
from tensorflow.python.keras.preprocessing.image import ImageDataGenerator
from tensorflow.python.keras.callbacks import TensorBoard
import time

dense_layers = [0,1,2]
layer_sizes = [16,32,64]
conv_layers = [4,5]
batch_sizes = [32,64]

taille_image = (96,96)
nb_epochs = 16

for batch_size in batch_sizes :
        for dense_layer in dense_layers:
                for layer_size in layer_sizes:
                        for conv_layer in conv_layers:
                                NAME = "{}-conv-{}-nodes-{}-dense-{}-batch-{}".format(conv_layer, layer_size, dense_layer,batch_size, int(time.time()))
                                tensorboard = TensorBoard(log_dir = 'Graph/{}'.format(NAME))
                                print(NAME)
                                model = Sequential()

                                model.add(Conv2D(layer_size, (3, 3), input_shape=(taille_image[0], taille_image[1], 3),padding = "same"))
                                model.add(Activation('relu'))
                                model.add(MaxPooling2D(pool_size=(2, 2)))

                                for l in range(conv_layer-1):
                                        model.add(Conv2D(layer_size, (3, 3), padding = "same"))
                                        model.add(Activation('relu'))
                                        model.add(Dropout(0.25))
                                        model.add(MaxPooling2D(pool_size=(2, 2)))
                                
                                model.add(Flatten())
                                for l in range(dense_layer):
                                        model.add(Dense(layer_size))
                                        model.add(Activation('relu'))

                                model.add(Dense(3))
                                model.add(Activation('softmax'))

                                model.compile(loss='categorical_crossentropy',
                                        optimizer='adam',
                                        metrics=['accuracy'])

                                train_datagen = ImageDataGenerator(
                                        rescale=1./255,
                                        shear_range=0.2,
                                        zoom_range=0.2,
                                        horizontal_flip=True,
                                        vertical_flip=True
                                )
                                valid_datagen = ImageDataGenerator(rescale=1./255)

                                test_datagen = ImageDataGenerator(rescale=1./255)

                                train_generator = train_datagen.flow_from_directory(
                                        directory='Images traitées/train',
                                        batch_size=batch_size,
                                        target_size=taille_image,
                                        color_mode="rgb",
                                        class_mode="categorical",
                                        shuffle=True,
                                        seed=42
                                )

                                validation_generator = valid_datagen.flow_from_directory(
                                        directory='Images traitées/validation',
                                        batch_size=1,
                                        target_size=taille_image,
                                        color_mode="rgb",
                                        class_mode="categorical",
                                        shuffle=True,
                                        seed=42
                                )

                                test_generator = test_datagen.flow_from_directory(
                                        directory='Images traitées/test',
                                        batch_size=1,
                                        target_size=taille_image,
                                        color_mode="rgb",
                                        class_mode=None,
                                        shuffle=False,
                                        seed=42
                                )

                                step_size_train = train_generator.n//train_generator.batch_size
                                step_size_valid = validation_generator.n//validation_generator.batch_size
                                step_size_test = test_generator.n//test_generator.batch_size

                                model.fit_generator(
                                        generator=train_generator,
                                        steps_per_epoch=step_size_train,
                                        validation_data=validation_generator,
                                        validation_steps = step_size_valid,
                                        epochs=nb_epochs,   
                                        callbacks = [tensorboard]
                                )