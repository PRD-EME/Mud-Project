import json
import operator

from tensorflow.python.keras.models import load_model
import numpy as np
from PIL import Image, ImageDraw, ImageColor

def Predire(img):
    seuil = 0.9
    image = Image.open(img)
    draw = ImageDraw.Draw(image, mode='RGBA')
    taille = 96
    diviseur=4
    stride = int(taille/diviseur)
    with open("classes_entrainees.json", "r") as open_file:
        classes = json.load(open_file)

    # On trie les classes du fichier json par ordre alphabétique pour que cela corresponde à l'odre des dossiers
    classes.sort(key=operator.itemgetter('classe'))
    
    liste_classes = []
    for classe in classes:
        liste_classes.append([classe, 0])

    x1 = 0
    y1 = 0
    x2 = taille
    y2 = taille
    line = 0
    col = 0

    if image.width%taille != 0:
        borderx = taille - image.width%taille
    else:
        borderx = 0
    
    if image.height%taille != 0:
        bordery = taille - image.height%taille
    else :
        bordery = 0
    # On créer une image blanche et on vient coller dessus notre image => on obtient des marges blanches
    image_resized = Image.new("RGB", (image.width+borderx, image.height+bordery), 'white')
    image_resized.paste(image)
    nb_vignette = (image_resized.width/taille)*(image_resized.height/taille)
    #On construit notre 3D array qui servira à localiser la détection
    detection_array=np.zeros([int(image_resized.height/stride),int(image_resized.width/stride),len(liste_classes)])
    #On transforme l'image en un numpy array pour pouvoir lancer la detection dessus
    scanned_image = np.array(image_resized)
    scanned_image = (scanned_image/255.0)
    
    model = load_model("my_model.h5")
    
    #Balayage Horizontal et création du detection array 
    while y2 <= image_resized.height:
        while x2 <= image_resized.width:
            input_windows = scanned_image[y1:y2, x1:x2, :]
            input_windows = np.expand_dims(input_windows, axis=0)
            y = model.predict(input_windows)
            
            #On formate les données pour avoir des 0 ou des 1 (pour pouvoir comparer plus tard)
            pos_of_max = y.argmax()
            y_binary = np.zeros(np.size(y))
            #Si on ne dépasse pas le seuil de détection, on met le tuple à (0,0,...,0)
            if (y[0][pos_of_max] > seuil):
                y_binary[pos_of_max] = 1
            detection_array[line][col][:] = y_binary
            x1 += stride
            x2 += stride
            col +=1
            
        x1 = 0
        x2 = taille
        y1 += stride
        y2 += stride
        line +=1
        col=0
    
    # on élimine les doublons pour chaque classe et on colorie l'image (condition).all() permet de comparer deux tuples 

    # On colore l'image 
    for row in range (0,detection_array.shape[0]-diviseur+1):
        for col in range (0,detection_array.shape[1]-diviseur+1):
            if (detection_array[row][col] == np.zeros((1, len(liste_classes)))).all(): 
                continue
            else:
                x1 = col*stride
                y1 = row*stride
                x2 = col*stride+taille
                y2 = row*stride+taille
                box = (x1,y1,x2,y2)
                prediction = detection_array[row][col]

                #On élimine les doublons en dessous
                for i in range(1,int(diviseur)):
                    for j in range(int(diviseur)-1,-int(diviseur), -1):
                        if (np.array_equal(prediction,detection_array[row+i][col+j])):
                            detection_array[row+i][col+j] = np.zeros((1, len(liste_classes)))
                #On élimine les doublons sur la ligne
                for j in range (1,int(diviseur)):
                    if (np.array_equal(prediction,detection_array[row][col+j])):
                        detection_array[row][col+j] = np.zeros((1, len(liste_classes)))

                vecteur = np.zeros((1, len(liste_classes)))

                for i in range(len(liste_classes)):
                    vecteur[0][i] = 1
                    if ((prediction == vecteur).all()):
                        liste_classes[i][1] += 1
                        couleur = ImageColor.getrgb(liste_classes[i][0]['couleur']) + (50,)
                        # On trace les rectangles avec la couleur correspondant à celle de la classe, sauf si la classe s'appelle
                        # "vide", dans ce cas là on n'affiche pas les rectangles
                        if liste_classes[i][0]['classe'].lower() != 'vide':
                            draw.rectangle(box, outline=liste_classes[i][0]['couleur'], fill=couleur)
                    vecteur[0][i] = 0                 

    return image, liste_classes, nb_vignette