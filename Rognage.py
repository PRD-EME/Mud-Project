from os.path import splitext

from PIL import Image
from numpy.random import randint

def Creer_vignette(name, coords, train, validation):
    nom_image = splitext(name.split('/')[-1])[0]
    img = Image.open(name)

    index = 0
    for pos in coords:

        classe = str(pos[0])

        x1 = float(pos[1])*img.width - 48
        y1 = float(pos[2])*img.height - 48
        x2 = float(pos[1])*img.width + 48
        y2 = float(pos[2])*img.height + 48

        if x1 < 0:
            x1 = 0
            x2 = 96
        if y1 < 0:
            y1 = 0
            y2 = 96
        if x2 > img.width:
            x2 = img.width
            x1 = x2-96
        if y2 > img.height:
            y2 = img.height
            y1 = y2-96

        box = (x1, y1, x2, y2)
        vignette = img.crop(box)

        # On envoie 20% des vignettes dans le dossier validation
        dispatch = randint(1, 6)

        if dispatch == 1:
            vignette.save(validation + '/' + classe + '/' + nom_image + '_' + str(index) + '.jpg')
        else:
            vignette.save(train + '/' + classe + '/' + nom_image + '_' + str(index) + '.jpg')

        index += 1