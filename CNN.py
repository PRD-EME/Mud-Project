import json

from tensorflow.python.keras.models import Sequential
from tensorflow.python.keras.layers import Conv2D, MaxPooling2D
from tensorflow.python.keras.layers import Activation, Dropout, Flatten, Dense
from tensorflow.python.keras.callbacks import TensorBoard, Callback
from tensorflow.python.keras.preprocessing.image import ImageDataGenerator
import numpy as np
import pandas as pd
import time

taille_image = (96,96)      
batch_size = 32 

def Entrainer(etat, val_entrainement, val_validation, barre, nb_epochs, classes, dossier_entrainement, dossier_validation): 
        model = Sequential()

        model.add(Conv2D(16, (3, 3), input_shape=(taille_image[0], taille_image[1], 3),padding = "same"))
        model.add(Activation('relu'))
        model.add(MaxPooling2D(pool_size=(2, 2)))

        model.add(Conv2D(32, (3, 3), padding = "same"))
        model.add(Activation('relu'))
        model.add(Dropout(0.25))
        model.add(MaxPooling2D(pool_size=(2, 2)))

        model.add(Conv2D(64, (3, 3), padding = "same"))
        model.add(Activation('relu'))
        model.add(Dropout(0.25))
        model.add(MaxPooling2D(pool_size=(2, 2)))

        model.add(Conv2D(128, (3, 3), padding = "same"))
        model.add(Activation('relu'))
        model.add(Dropout(0.25))
        model.add(MaxPooling2D(pool_size=(2, 2)))

        model.add(Conv2D(256, (3, 3), padding = "same"))
        model.add(Activation('relu'))
        model.add(Dropout(0.25))
        model.add(MaxPooling2D(pool_size=(2, 2)))

        model.add(Flatten())                
        model.add(Dense(len(classes)))
        model.add(Activation('softmax'))

        model.compile(loss='categorical_crossentropy',
                optimizer='adam',
                metrics=['accuracy'])
        
        # On crée un callback pour permettre l'affichage de différentes informations sur l'interface
        class My_Callback(Callback):
                def on_train_begin(self, logs={}):
                        self.accuracy = []
                        self.val_accuracy = []
                        etat.configure(text="Entraînement en cours")
                        return
 
                def on_epoch_end(self, epoch, logs={}):
                        barre.step(1)
                        barre.update()
                        self.accuracy.append(logs.get('acc'))
                        self.val_accuracy.append(logs.get('val_acc'))
                        return
                
                def on_train_end(self, logs={}):
                        etat.configure(text="Entraînement terminé")
                        val_entrainement.configure(text=str(round(self.accuracy[-1]*100, 2)) + ' %')
                        val_validation.configure(text=str(round(self.val_accuracy[-1]*100, 2)) + ' %')
                        return

        train_datagen = ImageDataGenerator(
                rescale=1./255,
                shear_range=0.2,
                zoom_range=0.2,
                horizontal_flip=True,
                vertical_flip=True
        )
        train_generator = train_datagen.flow_from_directory(
                directory=dossier_entrainement,
                batch_size=batch_size,
                target_size=taille_image,
                color_mode="rgb",
                class_mode="categorical",
                shuffle=True,
                seed=42
        )
        
        valid_datagen = ImageDataGenerator(rescale=1./255)
        validation_generator = valid_datagen.flow_from_directory(
                directory=dossier_validation,
                batch_size=1,
                target_size=taille_image,
                color_mode="rgb",
                class_mode="categorical",
                shuffle=True,
                seed=42
        )

        # Pour utiliser la fonction de test, décommenter les 3 parties commentées et mettre des vignettes dans le dossier
        # Images traitées/test/Images_test
        '''test_datagen = ImageDataGenerator(rescale=1./255)
        test_generator = test_datagen.flow_from_directory(
                directory='Images traitées/test',
                batch_size=1,
                target_size=taille_image,
                color_mode="rgb",
                class_mode=None,
                shuffle=False,
                seed=42
        )'''

        #NAME = "16,32,64,128,256-conv-{}-batchs-{}".format(batch_size,int(time.time()))
        #tensorboard = TensorBoard(log_dir = 'Graph/{}'.format(NAME))
        majCallback = My_Callback()
        
        step_size_train = train_generator.n//train_generator.batch_size
        step_size_valid = validation_generator.n//validation_generator.batch_size
        #step_size_test = test_generator.n//test_generator.batch_size

        model.fit_generator(
                generator=train_generator,
                steps_per_epoch=step_size_train,
                validation_data=validation_generator,
                validation_steps = step_size_valid,
                epochs=nb_epochs,
                #callbacks = [tensorboard, majCallback]
                callbacks = [majCallback]
        )
        model.save("my_model.h5")
        
        # Evaluation du model sur le dossier Validation
        model.evaluate_generator(generator=validation_generator,steps=step_size_valid,verbose=1)
        
        # Enregistre les classes utilisées lors de l'entrainement qui serviront lors de l'analyse
        with open("classes.json", "w", encoding="utf8") as write_file:
            json.dump(classes, write_file, ensure_ascii=False, indent=4)

        '''test_generator.reset()
        #On fait une prédiction sur une base de test réservée et on créer un CSV récapitulant les prédictions
        pred=model.predict_generator(test_generator,verbose=1, steps=step_size_test)
        predicted_class_indices = np.argmax(pred,axis=1)

        labels = (train_generator.class_indices)
        labels = dict((v,k) for k,v in labels.items())

        predictions = [labels[k] for k in predicted_class_indices]
        filenames=test_generator.filenames
        results=pd.DataFrame({"Filename":filenames, "Predictions":predictions})
        results.to_csv("Images traitées/test/{}.csv".format(NAME),index=False)'''