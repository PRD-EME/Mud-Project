from os import makedirs, listdir, remove, environ
from os.path import abspath, exists, splitext, join
from shutil import copy, rmtree
from tkinter import Tk, Label, Toplevel, Canvas, Listbox, Entry, ACTIVE, FALSE, END, PhotoImage
from tkinter.filedialog import askdirectory
from tkinter.font import Font
from tkinter.ttk import Style, Button, Progressbar
import json

from PIL import ImageTk, Image

import Rognage
import CNN
import Detection

# Liste des répertoires nécessaires au fonctionnement de l'application
BA = join(environ["USERPROFILE"], "Desktop/Base d'apprentissage")
IT = join(environ["USERPROFILE"], "Desktop/Images traitées")
IR = join(environ["USERPROFILE"], "Desktop/Images rejetées")

IT_TR = join(IT, "train")
IT_VA = join(IT, "validation")
IT_TE = join(IT, "test")
TE_TE = join(IT_TE, "Images_test")

# Icône de l'application
ico = abspath('eme.ico')

# Création des répertoires s'ils n'existent pas déjà
if not exists(BA):
    makedirs(BA)
if not exists(IT):
    makedirs(IT)
if not exists(IR):
    makedirs(IR)

if not exists(IT_TR):
    makedirs(IT_TR)
if not exists(IT_VA):
    makedirs(IT_VA)
if not exists(IT_TE):
    makedirs(IT_TE)
if not exists(TE_TE):
    makedirs(TE_TE)

#################################################################################################################################
# Méthodes relatives à la création de fenêtres 
#################################################################################################################################

#--------------------------------------------------------------------------------------------------------------------------------
# Permet de définir les propriétés de la fenêtre
#--------------------------------------------------------------------------------------------------------------------------------
def Definir_geometrie(racine, texte, width, height, nbcolonnes, nblignes):
    racine.title(texte)
    racine.iconbitmap(ico)
    racine.resizable(width=False, height=False)

    # Positions permettant de centrer la fenêtre. Il y a un offset de 30 pour compenser la barre des tâches
    posx = (racine.winfo_screenwidth()-width)/2
    posy = (racine.winfo_screenheight()-height)/2 - 30

    if height == racine.winfo_screenheight:
        posy += 30

    racine.geometry('%dx%d+%d+%d' % (width, height, posx, posy))

    # Rend les cases de la grille adaptables en fonction de la taille de la fenêtre
    racine.grid()
    rows = 0
    while rows < nblignes:
        racine.rowconfigure(rows, weight=1)
        rows += 1

    columns = 0
    while columns < nbcolonnes:
          racine.columnconfigure(rows, weight=1)
          columns += 1

    racine.deiconify()

#--------------------------------------------------------------------------------------------------------------------------------
# Création de texte
#--------------------------------------------------------------------------------------------------------------------------------
def Ajouter_texte(racine, texte, posc, posr, span, stick):
    label = Label(racine, text=texte)
    label.grid(column=posc, row=posr, columnspan=span, sticky=stick)

    return label

#--------------------------------------------------------------------------------------------------------------------------------
# Création de bouton
#--------------------------------------------------------------------------------------------------------------------------------
def Ajouter_bouton(racine, texte, aspect, action, posc, posr, span):
    bouton = Button(racine, text=texte, style=aspect, command=action)
    bouton.grid(column=posc, row=posr, columnspan=span, padx=20, sticky='ew')

    return bouton

#--------------------------------------------------------------------------------------------------------------------------------
# Création de canvas
#--------------------------------------------------------------------------------------------------------------------------------
def Ajouter_canvas(racine, largeur, hauteur, couleur, posc, posr, cspan, rspan):
    canvas = Canvas(racine, width=largeur, height=hauteur, bg=couleur)
    canvas.grid(column=posc, row=posr, columnspan=cspan, rowspan=rspan)

    return canvas

#--------------------------------------------------------------------------------------------------------------------------------
# Création d'une liste de choix
#--------------------------------------------------------------------------------------------------------------------------------
def Ajouter_listbox(racine, posc, posr):
    listebox = Listbox(racine)
    listebox.grid(column=posc, row=posr)

    return listebox

#--------------------------------------------------------------------------------------------------------------------------------
# Permet d'ouvrir une image et de la rendre compatible avec les canvas Tkinter
#--------------------------------------------------------------------------------------------------------------------------------
def Preparer_image(image, largeur, hauteur):
    img = Image.open(image)
    img.thumbnail((largeur, hauteur))
    photo = ImageTk.PhotoImage(img)

    return photo
    
#################################################################################################################################
# Méthodes relatives aux différents modes de fonctionnement de l'application
#################################################################################################################################

#--------------------------------------------------------------------------------------------------------------------------------
# Mot de passe pour sécuriser l'application
#--------------------------------------------------------------------------------------------------------------------------------
def Se_Connecter(edit_text, texte):
    mdp = edit_text.get()

    if mdp == 'emeorgadetect':
        bouton_analyse.configure(state='enabled')
        bouton_entrainement.configure(state='enabled')
        texte_mdp.configure(text="Identification réussie")
        texte_mdp.grid(columnspan='4')
        edit_text.destroy()
        bouton_se_connecter.destroy()
        texte.destroy()
        Ajouter_texte(Racine, "                      ", 2, 3, 1, None)
    
    else:
        texte.configure(text="Mot de passe"+"\n"+"refusé")

#--------------------------------------------------------------------------------------------------------------------------------
# MODE ENTRAINEMENT : Accueil
#--------------------------------------------------------------------------------------------------------------------------------
def Mode_entrainement_accueil():
    global Entrainement
    Entrainement = Toplevel(Racine)
    # Ajout d'un protocole lorsque l'on ferme la fenêtre quand on appuie sur la croix
    Entrainement.protocol("WM_DELETE_WINDOW", Fermeture_entrainement)
    Entrainement.withdraw()
    
    entrainement_taille = (0.9*lecran, 0.9*hecran)
    Definir_geometrie(Entrainement, 'Mode entraînement', entrainement_taille[0], entrainement_taille[1], 3, 100)

    global ce_taille
    ce_taille = (0.8*entrainement_taille[0], 0.8*entrainement_taille[1])
    global ce
    ce = Ajouter_canvas(Entrainement, ce_taille[0], ce_taille[1], 'grey', 1, 0, 1, 95)

    Ajouter_bouton(Entrainement, 'Quitter', 'Red.TButton', Fermeture_entrainement, 2, 81, 1)
    global bouton_entrainer
    bouton_entrainer = Ajouter_bouton(Entrainement, 'Entrainer', 'Magenta.TButton', Entrainer, 2, 10, 1)
    global bouton_next
    bouton_next = Ajouter_bouton(Entrainement, 'Photo suivante', 'Green.TButton', Mode_entrainement_image_suivante, 2, 33, 1)
    global entrainement_txt
    entrainement_txt = Ajouter_texte(Entrainement, '', 2, 11, 1, 'w')
    Ajouter_texte(Entrainement, "", 1, 95, 1, None)
    
    vignettes = 0
    for sous_dos in listdir(IT_TR):
        vignettes += len(listdir(IT_TR + '/' + sous_dos))
    for sous_dos in listdir(IT_VA):
        vignettes += len(listdir(IT_VA + '/' + sous_dos))

    if vignettes < 500:
        bouton_entrainer.configure(state='disabled')
        entrainement_txt.configure(text="L'entraînement du"+"\n"+"réseau de neurones"+"\n"+"n'est disponible"+"\n"
                                    +"qu'à partir de 500"+"\n"+"vignettes")

    global boxliste
    boxliste = Ajouter_listbox(Entrainement, 0, 11)
    
    # On charge les données sur les classes contenues dans le json
    global organismes
    with open("classes.json", "rb") as open_file:
        organismes = json.load(open_file, encoding="utf-8")
    
    # Si des dossiers vignettes correspondant aux classes contenues dans le json ne sont pas présents, on les recréer
    for organisme in organismes:
        if not exists(IT_TR + '/' + organisme["classe"]):
            makedirs(IT_TR + '/' + organisme["classe"])
        if not exists(IT_VA + '/' + organisme["classe"]):
            makedirs(IT_VA + '/' + organisme["classe"])
        boxliste.insert('end', organisme["classe"])

    global classe_plus
    classe_plus = Ajouter_bouton(Entrainement, '+', 'Black.TButton', 
                                    lambda : Parametrer_classe(boxliste, 'add', organismes), 0, 12, 1)
    global classe_moins
    classe_moins = Ajouter_bouton(Entrainement, '-', 'Black.TButton', 
                                    lambda : Parametrer_classe(boxliste, 'del', organismes), 0, 13, 1)

    # Désactivation des boutons "+" et "-" en fonction du nombre de classes
    if boxliste.size() > 9:
        classe_plus.configure(state='disabled')
    if boxliste.size() < 1:
        classe_moins.configure(state='disabled')

    Ajouter_texte(Entrainement, "Type d'objet à détecter :", 0, 10, 1, 'w').configure(font=SG)
    Ajouter_texte(Entrainement, 'Raccourcis clavier :', 0, 30, 1, 'w').configure(font=SG)
    Ajouter_texte(Entrainement, 'Photo suivante : Espace', 0, 31, 1, 'w')
    Ajouter_texte(Entrainement, 'Annuler un rectangle : Echap', 0, 32, 1, 'w')
    Ajouter_texte(Entrainement, '', 0, 33, 1, 'w')
    Ajouter_texte(Entrainement, "Nom de l'image :", 0, 50, 1, 'w').configure(font=SG)
    Ajouter_texte(Entrainement, 'Nombre de vignettes :', 0, 60, 1, 'w').configure(font=SG)
    
    # Affichage automatique des noms des différentes classes
    ligne = 61
    for organisme in organismes:
        t = Ajouter_texte(Entrainement, organisme['classe'], 0, ligne, 1, 'w')
        t.configure(font=S)
        ligne += 2
    Ajouter_texte(Entrainement, 'TOTAL', 0, 83, 1, 'w').configure(font=S)
    
    # Affichage automatique du nombre de vignettes correspondant à chaque classe (dossier train + dossier validation)
    ligne = 62
    for organisme in organismes:
        Ajouter_texte(Entrainement, str(len(listdir(IT_TR+'/'+organisme['classe']))+
                                        len(listdir(IT_VA+'/'+organisme['classe']))), 0, ligne, 1, 'w')
        ligne += 2
    Ajouter_texte(Entrainement, str(vignettes), 0, 84, 1, 'w')

    # Si un fichier contenue dans la Base d'apprentissage n'est pas une image, on l'ignore
    global images_apprentissage
    images_apprentissage = listdir(BA)
    for fic in images_apprentissage:
        ext = splitext(fic)[1]
        if ext.lower() != '.jpg' and ext.lower() != '.jpeg' and ext.lower() != '.png' and ext.lower() != '.bmp':
            images_apprentissage.remove(fic)

    global index_image_apprentissage
    index_image_apprentissage = 0

    images_traitees = listdir(IT)
    images_traitees.remove('test')
    images_traitees.remove('train')
    images_traitees.remove('validation')

    images_rejetees = listdir(IR)

    # On liste les images dont les noms sont identiques avec celles présentes dans Images traitées et Images rejetées car elles
    # peuvent poser problème lorsqsue l'on veut les déplacer
    images_deja_traitees = images_traitees+images_rejetees
    images_doublon = []
    for fic_traite in images_deja_traitees:
        for fic_apprentissage in images_apprentissage:
            if fic_traite == fic_apprentissage:
                images_doublon.append(fic_apprentissage)

    images_doublon_light =[]
    if len(images_doublon) > 10:
        for i in range(0, 10):
            images_doublon_light.append(images_doublon[i])
        ce.create_text(ce_taille[0]/2, ce_taille[1]/2, text="Attention les images suivantes ont un nom déjà utilisé dans "
                            +"Morpheus/Images traitées ou Morpheus/Images rejetées. Merci de bien vouloir renommer les " 
                            +"images qui posent problème dans Morpheus/Base d'apprentissage : "+str(images_doublon_light)
                            +" + "+str(len(images_doublon)-10)+" autre(s) image(s).",
                            fill='red', width=ce_taille[0]-20, justify='center')


    elif images_doublon:
         ce.create_text(ce_taille[0]/2, ce_taille[1]/2, text="Attention les images suivantes ont un nom déjà utilisé dans "
                            +"Morpheus/Images traitées ou Morpheus/Images rejetées. Merci de bien vouloir renommer les " 
                            +"images qui posent problème dans Morpheus/Base d'apprentissage : "+str(images_doublon),
                            fill='red', width=ce_taille[0]-20, justify='center')


    elif images_apprentissage:
        # Affichage de la 1ère image
        emplacement_premiere_image = BA + "/" + images_apprentissage[index_image_apprentissage]
        ce.premiere_image = Preparer_image(emplacement_premiere_image, ce_taille[0], ce_taille[1])
        ce.create_image(0, 0, image=ce.premiere_image, anchor='nw')

        global nom_img_entrainement
        nom_img_entrainement = Ajouter_texte(Entrainement, emplacement_premiere_image.split('/')[-1], 0, 51, 1, 'w')
        Ajouter_texte(Entrainement, '', 0, 52, 1, 'w')

        # Association des actions utilisateur aux fonctions correspondantes
        ce.bind("<ButtonRelease-1>", clickgaucherelache)
        Entrainement.bind("<Escape>", retourarriere)
        Entrainement.bind("<space>", valider)

        Mode_entrainement_vignettage()

    else:
        ce.create_text(ce_taille[0]/2, ce_taille[1]/2, text="Pas d'images dans le répertoire : Morpheus/Base d'apprentissage.",
                            fill='red', width=ce_taille[0]-20, justify='center')
        bouton_next.configure(state='disabled')

#--------------------------------------------------------------------------------------------------------------------------------
# MODE ENTRAINEMENT : Permet de paramétrer les différentes classes
#--------------------------------------------------------------------------------------------------------------------------------
def Parametrer_classe(listebox, mode, organismes):
    global Paramclass
    Paramclass = Toplevel(Entrainement)
    Paramclass.withdraw()

    Definir_geometrie(Paramclass, 'Gestion des classes', 0.15*lecran, 0.25*hecran, 2, 4)

    e = Entry(Paramclass)
    e.grid(column=0, row=1, columnspan=2)

    alerte = Ajouter_texte(Paramclass, "", 0, 3, 2, None)

    if mode == 'add':
        txt = Ajouter_texte(Paramclass, "Rentrer le nom de la classe à ajouter", 0, 0, 2, None)
        val = Ajouter_bouton(Paramclass, 'Valider', 'Green.TButton', 
                                lambda : Nommer_classe(alerte, e, listebox, val, txt), 0, 2, 2)

    if mode == 'del':
        txt = Ajouter_texte(Paramclass, "Rentrer le nom de la classe à supprimer", 0, 0, 2, None)
        val = Ajouter_bouton(Paramclass, 'Supprimer', 'Green.TButton', lambda : Supprimer_classe(e, listebox), 0, 2, 2)

#--------------------------------------------------------------------------------------------------------------------------------
# MODE ENTRAINEMENT : Permet de nommer une nouvelle classe
#--------------------------------------------------------------------------------------------------------------------------------
def Nommer_classe(alerte, edit_text, listebox, bouton_valider, texte):
    nom_classe = edit_text.get()

    for organisme in organismes:
        if (not nom_classe) or (nom_classe.isspace()) or ('/' in nom_classe):
            alerte.configure(text="Ce nom n'est pas valide")
            return
        elif organisme['classe'].lower() == nom_classe.lower():
            alerte.configure(text="Ce nom est déjà utilisé")
            return
    
    alerte.destroy()
    bouton_valider.destroy()
    edit_text.destroy()
    texte.configure(text='Classe '+nom_classe)
    Colorer_classe(alerte, nom_classe, listebox)

#--------------------------------------------------------------------------------------------------------------------------------
# MODE ENTRAINEMENT : Permet d'associer une couleur à une nouvelle classe
#--------------------------------------------------------------------------------------------------------------------------------
def Colorer_classe(texte, nom_classe, listebox):
    texte.destroy()
    Definir_geometrie(Paramclass, 'Gestion des classes', 0.2*lecran, 0.6*hecran, 2, 8)
    Ajouter_texte(Paramclass, "Sélectionner la couleur", 0, 1, 2, None)
    bleu = Ajouter_bouton(Paramclass, "", 'BackBlue.TButton', 
                            lambda : Afficher_couleur(canevas, 'blue', nom_classe, listebox), 0, 2, 1)
    rouge = Ajouter_bouton(Paramclass, "", 'BackRed.TButton', 
                            lambda : Afficher_couleur(canevas,'red', nom_classe, listebox), 0, 3, 1)
    vert = Ajouter_bouton(Paramclass, "", 'BackGreen.TButton', 
                            lambda : Afficher_couleur(canevas,'green', nom_classe, listebox), 0, 4, 1)
    blanc = Ajouter_bouton(Paramclass, "", 'BackWhite.TButton', 
                            lambda : Afficher_couleur(canevas,'white', nom_classe, listebox), 0, 5, 1)
    noir = Ajouter_bouton(Paramclass, "", 'BackBlack.TButton', 
                            lambda : Afficher_couleur(canevas,'black', nom_classe, listebox), 0, 6, 1)
    jaune = Ajouter_bouton(Paramclass, "", 'BackYellow.TButton', 
                            lambda : Afficher_couleur(canevas,'yellow', nom_classe, listebox), 1, 2, 1)
    rose = Ajouter_bouton(Paramclass, "", 'BackPink.TButton', 
                            lambda : Afficher_couleur(canevas,'pink', nom_classe, listebox), 1, 3, 1)
    cyan = Ajouter_bouton(Paramclass, "", 'BackCyan.TButton', 
                            lambda : Afficher_couleur(canevas,'cyan', nom_classe, listebox), 1, 4, 1)
    orange = Ajouter_bouton(Paramclass, "", 'BackOrange.TButton', 
                            lambda : Afficher_couleur(canevas,'orange', nom_classe, listebox), 1, 5, 1)
    magenta = Ajouter_bouton(Paramclass, "", 'BackMagenta.TButton', 
                            lambda : Afficher_couleur(canevas,'magenta', nom_classe, listebox), 1, 6, 1)
    Ajouter_texte(Paramclass, "Couleur sélectionnée", 0, 7, 1, None)
    canevas = Ajouter_canvas(Paramclass, 50, 25, None, 1, 7, 1, 1)

    for organisme in organismes:
        if organisme['couleur'] == 'blue':
            bleu.configure(state='disabled', style='Grey.TButton', text='Déjà utilisé')
        if organisme['couleur'] == 'red':
            rouge.configure(state='disabled', style='Grey.TButton', text='Déjà utilisé')
        if organisme['couleur'] == 'green':
            vert.configure(state='disabled', style='Grey.TButton', text='Déjà utilisé')
        if organisme['couleur'] == 'white':
            blanc.configure(state='disabled', style='Grey.TButton', text='Déjà utilisé')
        if organisme['couleur'] == 'black':
            noir.configure(state='disabled', style='Grey.TButton', text='Déjà utilisé')
        if organisme['couleur'] == 'yellow':
            jaune.configure(state='disabled', style='Grey.TButton', text='Déjà utilisé')
        if organisme['couleur'] == 'pink':
            rose.configure(state='disabled', style='Grey.TButton', text='Déjà utilisé')
        if organisme['couleur'] == 'cyan':
            cyan.configure(state='disabled', style='Grey.TButton', text='Déjà utilisé')
        if organisme['couleur'] == 'orange':
            orange.configure(state='disabled', style='Grey.TButton', text='Déjà utilisé')
        if organisme['couleur'] == 'magenta':
            magenta.configure(state='disabled', style='Grey.TButton', text='Déjà utilisé')

#--------------------------------------------------------------------------------------------------------------------------------
# MODE ENTRAINEMENT : Permet d'afficher la couleur sélectionnée
#--------------------------------------------------------------------------------------------------------------------------------           
def Afficher_couleur(canevas, color, name, listebox):
    canevas.delete('all')
    canevas.create_rectangle(0, 0, 50, 25, fill=color)

    Ajouter_bouton(Paramclass, "Terminer", 'Green.TButton', lambda : Valider_classe(color, name, listebox), 0, 9, 2)

#--------------------------------------------------------------------------------------------------------------------------------
# MODE ENTRAINEMENT : Permet de valider la création d'une nouvelle classe
#-------------------------------------------------------------------------------------------------------------------------------- 
def Valider_classe(color, name, listebox):
    global organismes
    listebox.insert('end', name)
    makedirs(IT_TR + '/' + name)
    makedirs(IT_VA + '/' + name)
    organismes.append({
        "classe": name,
        "couleur": color
    })

    with open("classes.json", "w", encoding="utf8") as write_file:
            json.dump(organismes, write_file, ensure_ascii=False, indent=4)
    if listebox.size() == 10:
        classe_plus.configure(state='disabled')
    if listebox.size() > 0:
        classe_moins.configure(state='enabled')

    Paramclass.destroy()
#--------------------------------------------------------------------------------------------------------------------------------
# MODE ENTRAINEMENT : Permet de supprimer une classe
#-------------------------------------------------------------------------------------------------------------------------------- 
def Supprimer_classe(edit_text, listebox):
    nom_classe = edit_text.get()

    rectangles_a_supprimer = []
    for organisme in organismes:
        if organisme['classe'].lower() == nom_classe.lower():
            for i in range(listebox.size()):
                if str(listebox.get(i).lower()) == nom_classe.lower():
                    listebox.delete(i)
            rmtree(IT_TR + '/' + nom_classe)
            rmtree(IT_VA + '/' + nom_classe)
            organismes.remove(organisme)
            with open("classes.json", "w", encoding="utf8") as write_file:
                json.dump(organismes, write_file, ensure_ascii=False, indent=4)
            try:
                for rectangle in liste_rectangles:
                    if ce.itemcget(rectangle[0], "fill") == organisme['couleur']:
                        rectangles_a_supprimer.append(rectangle)
                        ce.delete(rectangle[0])
                for rectangle in rectangles_a_supprimer:
                    liste_rectangles.remove(rectangle)
            except NameError:
                pass
            if listebox.size() == 0:
                classe_moins.configure(state='disabled')
            if listebox.size() < 10:
                classe_plus.configure(state='enabled')
            Paramclass.destroy()
            return
    
    Ajouter_texte(Paramclass, "Aucune classe ne porte ce nom", 0, 3, 2, None)

#--------------------------------------------------------------------------------------------------------------------------------
# MODE ENTRAINEMENT : Permet l'encadrement des organismes
#--------------------------------------------------------------------------------------------------------------------------------
def Mode_entrainement_vignettage():
    global liste_rectangles
    liste_rectangles = []

    # Si le dossier n'est pas vide...
    if index_image_apprentissage < len(images_apprentissage):
        global emplacement_image
        emplacement_image =  BA + "/" + images_apprentissage[index_image_apprentissage]

        global image_affichee_originale
        image_affichee_originale = Image.open(emplacement_image)
        global image_affichee
        image_affichee = image_affichee_originale.copy()

        nom_img_entrainement.configure(text=images_apprentissage[index_image_apprentissage].split('/')[-1])

        image_affichee.thumbnail((ce_taille[0], ce_taille[1]))
        ce.photo_affichee = ImageTk.PhotoImage(image_affichee)
        ce.delete('all')
        ce.create_image(0, 0, image=ce.photo_affichee, anchor='nw')

    # Si le dossier est vide...
    else:
        ce.delete('all')
        bouton_next.configure(state='disabled')
        nom_img_entrainement.destroy()
        ce.create_text(ce_taille[0]/2, ce_taille[1]/2, text="Plus d'images dans le répertoire : Morpheus/Base d'apprentissage.",
                                             fill='red', width=ce_taille[0]-20, justify='center')
        ce.unbind("<ButtonRelease-1>")
        Entrainement.unbind("<Escape>")
        Entrainement.unbind("<space>")

#--------------------------------------------------------------------------------------------------------------------------------
# MODE ENTRAINEMENT : Entrainement du réseau de neurones
#--------------------------------------------------------------------------------------------------------------------------------
def Entrainer():
    bouton_entrainer.configure(state='disabled')
    classe_plus.configure(state='disabled')
    classe_moins.configure(state='disabled')

    ce.unbind("<ButtonRelease-1>")
    Entrainement.unbind("<Escape>")
    Entrainement.unbind("<space>")

    nb_epochs = 16

    etat_entrainement = Ajouter_texte(Entrainement, "Début de l'entraînement", 0, 95, 1, 'ew')
    Ajouter_texte(Entrainement, "Précision sur la "+"\n"+"base d'entraînement", 2, 12, 1, 'w')
    val_entrainement = Ajouter_texte(Entrainement, "", 2, 13, 1, 'w')
    Ajouter_texte(Entrainement, "Précision sur la"+"\n"+"base de validation", 2, 14, 1, 'w')
    val_validation = Ajouter_texte(Entrainement, "", 2, 15, 1, 'w')

    barre = Progressbar(Entrainement, style='Blue.Horizontal.TProgressbar', length=lecran/2, mode='determinate', 
                        maximum=nb_epochs+10**-10)
    barre.grid(column=1, row=95, columnspan=1, stick='we')
    barre.update()

    CNN.Entrainer(etat_entrainement, val_entrainement, val_validation, barre, nb_epochs, organismes, IT_TR, IT_VA)

    ce.bind("<ButtonRelease-1>", clickgaucherelache)
    Entrainement.bind("<Escape>", retourarriere)
    Entrainement.bind("<space>", valider)

    bouton_entrainer.configure(state='enabled')
    classe_plus.configure(state='enabled')
    classe_moins.configure(state='enabled')

#--------------------------------------------------------------------------------------------------------------------------------
# MODE ENTRAINEMENT : Passage à l'image suivante
#--------------------------------------------------------------------------------------------------------------------------------
def Mode_entrainement_image_suivante():
    global index_image_apprentissage

    if liste_rectangles:
        coords = Creer_coordonnees(liste_rectangles)
        Rognage.Creer_vignette(emplacement_image, coords, IT_TR, IT_VA)
        copy(emplacement_image, IT)
        remove(emplacement_image)
        
    else:
        copy(emplacement_image, IR)
        remove(emplacement_image)

    liste_rectangles.clear()

    vignettes = 0
    for sous_dos in listdir(IT_TR):
        vignettes += len(listdir(IT_TR + '/' + sous_dos))
    for sous_dos in listdir(IT_VA):
        vignettes += len(listdir(IT_VA + '/' + sous_dos))

    ligne = 61
    for organisme in organismes:
        t = Ajouter_texte(Entrainement, organisme['classe'], 0, ligne, 1, 'w')
        t.configure(font=S)
        ligne += 2
    Ajouter_texte(Entrainement, 'TOTAL', 0, 83, 1, 'w').configure(font=S)
    
    ligne = 62
    for organisme in organismes:
        Ajouter_texte(Entrainement, str(len(listdir(IT_TR+'/'+organisme['classe']))+
                                            len(listdir(IT_VA+'/'+organisme['classe']))), 0, ligne, 1, 'w')
        ligne += 2
    Ajouter_texte(Entrainement, str(vignettes), 0, 84, 1, 'w')

    if vignettes >= 500:
        bouton_entrainer.configure(state='enabled')
        entrainement_txt.configure(text='')
    
    index_image_apprentissage += 1

    Mode_entrainement_vignettage()

#--------------------------------------------------------------------------------------------------------------------------------
# MODE ENTRAINEMENT / EVENT : clique gauche relâché
#--------------------------------------------------------------------------------------------------------------------------------
def clickgaucherelache(event) :
    # L'image affichée dans le canvas est plus petite que sa taille originale donc il faut prendre en compte le changement
    # d'échelle quand on calcule les coordonées des vignettes
    ratio = image_affichee.width/image_affichee_originale.width
    tlx = event.x-48*(ratio)
    tly = event.y-48*(ratio)
    brx = event.x+48*(ratio)
    bry = event.y+48*(ratio)

    # Comme on crée un carré autour du curseur de la souris, on fait des tests pour voir si on est trop proche du bord de l'image
    # pour ne pas dépasser
    if tlx < 0:
        tlx = 0
        brx = 96*(ratio)
    if tly < 0:
        tly = 0
        bry = 96*(ratio)
    if brx > image_affichee.width:
        brx = image_affichee.width
        tlx = brx-96*(ratio)
    if bry > image_affichee.height:
        bry = image_affichee.height
        tly = bry-96*(ratio)

    for organisme in organismes:
        if organisme["classe"] == boxliste.get(ACTIVE):
            couleur = organisme["couleur"]

    r = ce.create_rectangle(tlx, tly, brx, bry, outline=couleur, fill=couleur, stipple="gray12")

    liste_rectangles.append([r, event.x, event.y])

#--------------------------------------------------------------------------------------------------------------------------------
# MODE ENTRAINEMENT / EVENT : touche Échap appuyée
#--------------------------------------------------------------------------------------------------------------------------------
def retourarriere(event):
    if liste_rectangles:
        ce.delete(liste_rectangles[-1][0])
        del liste_rectangles[-1]

#--------------------------------------------------------------------------------------------------------------------------------
# MODE ENTRAINEMENT / EVENT : touche Espace appuyée
#--------------------------------------------------------------------------------------------------------------------------------
def valider(event):
    Mode_entrainement_image_suivante()

#--------------------------------------------------------------------------------------------------------------------------------
# MODE ENTRAINEMENT : Création du fichier txt avec les données relatives aux rectangles tracés
#--------------------------------------------------------------------------------------------------------------------------------
def Creer_coordonnees(donnees):
    coordonnees = []
    for coord in donnees:
        for organisme in organismes:
            if organisme['couleur'] == ce.itemcget(coord[0], "fill"):
                classe = organisme['classe']

        centre_rectangle_relatif_x = coord[1]/image_affichee.width
        centre_rectangle_relatif_y = coord[2]/image_affichee.height
        coordonnees.append((classe, centre_rectangle_relatif_x, centre_rectangle_relatif_y))

    return coordonnees
    
#--------------------------------------------------------------------------------------------------------------------------------
# MODE ENTRAINEMENT : Quitter le mode entrainement
#--------------------------------------------------------------------------------------------------------------------------------
def Fermeture_entrainement():
    Entrainement.destroy()
    bouton_analyse.configure(state='normal')
    bouton_entrainement.configure(state='normal')
    bouton_quitter.configure(state='normal')

#--------------------------------------------------------------------------------------------------------------------------------
# MODE ANALYSE / FENETRE : Affichage de la 1ère image
#--------------------------------------------------------------------------------------------------------------------------------
def Mode_analyse_accueil():
    global Analyse
    Analyse = Toplevel(Racine)
    Analyse.protocol("WM_DELETE_WINDOW", Fermeture_analyse)
    Analyse.withdraw()
    
    bouton_analyse.configure(state='disabled')
    bouton_entrainement.configure(state='disabled')
    bouton_quitter.configure(state='disabled')

    global MODE
    MODE = 'Pre-analyse'

    global index_image_analyse
    index_image_analyse = 0

    global images_a_analyser
    images_a_analyser = Ouvrir_images()

    # Si on ne sélectionne aucun dossier, on revient à la fenêtre d'accueil
    if images_a_analyser is None:
        Fermeture_analyse()

    else:
        analyse_taille = (0.85*lecran, 0.9*hecran)
        Definir_geometrie(Analyse, 'Mode analyse', analyse_taille[0], analyse_taille[1], 6, 100)    
        Ajouter_texte(Analyse, "Emplacement du dossier : ", 0, 0, 1, 'w')
        Ajouter_texte(Analyse, repertoire_analyse, 2, 0, 1, 'w')
        global bouton_lancer_analyse
        bouton_lancer_analyse = Ajouter_bouton(Analyse, "Lancer l'analyse", 'Green.TButton', Mode_analyse_execution, 0, 90, 1)
        global bouton_precedente
        bouton_precedente = Ajouter_bouton(Analyse, '<', 'Black.TButton', Precedente, 1, 90, 1)
        global bouton_suivante
        bouton_suivante = Ajouter_bouton(Analyse, '>', 'Black.TButton', Suivante, 3, 90, 1)
        Ajouter_bouton(Analyse, 'Quitter', 'Red.TButton', Fermeture_analyse, 4, 90, 1)
        Ajouter_texte(Analyse, "Au global", 5, 10, 1, 'w').configure(font=SG)
        Ajouter_texte(Analyse, "Sur l'image considérée", 5, 30, 1, 'w').configure(font=SG)
        Ajouter_texte(Analyse, "", 1, 95, 4, None)

        global ca_taille
        ca_taille = (0.8*analyse_taille[0], 0.8*analyse_taille[1])
        global ca
        ca = Ajouter_canvas(Analyse, ca_taille[0], ca_taille[1], 'grey', 0, 1, 5, 89)

        if images_a_analyser:
            global nom_img_analyse
            nom_img_analyse = Ajouter_texte(Analyse, images_a_analyser[index_image_analyse].split('/')[-1], 2, 90, 1, None)

            index = 0
            for i in images_a_analyser:
                images_a_analyser[index] = repertoire_analyse + '/' + i
                index += 1

            if index_image_analyse == 0:
                bouton_precedente.configure(state='disabled')
    
            if index_image_analyse == len(images_a_analyser)-1:
                bouton_suivante.configure(state='disabled')

            img = images_a_analyser[index_image_analyse]
            ca.photo = Preparer_image(img, ca_taille[0], ca_taille[1])
            ca.create_image(0, 0, image=ca.photo, anchor='nw')


        else:
            ca.create_text(ca_taille[0]/2, ca_taille[1]/2, text="Le dossier choisi ne contient pas d'images JPG, PNG ou BMP.",
                            fill='red', width=ca_taille[0]-20, justify='center')
            bouton_lancer_analyse.configure(state='disabled')  
            bouton_precedente.configure(state='disabled')
            bouton_suivante.configure(state='disabled')            

#--------------------------------------------------------------------------------------------------------------------------------
# MODE ANALYSE : Ouverture du répertoire contenant les images à analyser
#--------------------------------------------------------------------------------------------------------------------------------
def Ouvrir_images():
    global repertoire_analyse
    repertoire_analyse = askdirectory()

    # On récupère les images situées dans le dossier sélectionné et on ignore les autres fichiers
    if repertoire_analyse:    
        liste_images = listdir(repertoire_analyse)

        for fic in liste_images:
            ext = splitext(fic)[-1]
            if ext.lower() != '.jpg' and ext.lower() != '.jpeg' and ext.lower() != '.png' and ext.lower() != '.bmp':
                liste_images.remove(fic)

        return liste_images

#--------------------------------------------------------------------------------------------------------------------------------
# MODE ANALYSE : Enregistrement des images dans un sous-répertoire 'Images analysées'
#--------------------------------------------------------------------------------------------------------------------------------
def Enregistrer_image():
    # On crée un sous-dossier dans celui que l'on a sélectionné et on y enregistre toutes les images analysées
    repertoire_sauvegarde = repertoire_analyse + '/' + 'Images analysées'
    
    if not exists(abspath(repertoire_sauvegarde)):
        makedirs(repertoire_sauvegarde)
    
    i = 0
    for img in images_analysees:
        nom = images_a_analyser[i].split('/')[-1]
        img.save(repertoire_sauvegarde + '/' + nom)
        i += 1

#--------------------------------------------------------------------------------------------------------------------------------
# MODE ANALYSE : Affichage de l'image précédente
#--------------------------------------------------------------------------------------------------------------------------------
def Precedente():
    global index_image_analyse

    if index_image_analyse > 0:
        bouton_suivante.configure(state='normal', style='Black.TButton')
        index_image_analyse -= 1
        ca.delete('all')
        
        if MODE == 'Pre-analyse':
            img = images_a_analyser[index_image_analyse]
            ca.photo = Preparer_image(img, ca_taille[0], ca_taille[1])
            ca.create_image(0, 0, image=ca.photo, anchor='nw')

        if MODE == 'Post-analyse':
            img = images_analysees[index_image_analyse]
            img.thumbnail((ca_taille[0], ca_taille[1]))
            ca.photo_analysee = ImageTk.PhotoImage(image=img)
            ca.create_image(0, 0, image=ca.photo_analysee, anchor='nw')
            ligne = 31
            for classe in liste_classes[index_image_analyse]:
                txt_classes[ligne-31].configure(text=str(classe[1])+' soit '+
                                                str(round(classe[1]/liste_nb_vignettes[index_image_analyse]*100,2))+' %')
                ligne += 1
    
    nom_img_analyse.configure(text=images_a_analyser[index_image_analyse].split('/')[-1])

    if index_image_analyse == 0:
        bouton_precedente.configure(state='disabled')

#--------------------------------------------------------------------------------------------------------------------------------
# MODE ANALYSE : Affichage de l'image suivante
#--------------------------------------------------------------------------------------------------------------------------------
def Suivante():
    global index_image_analyse

    if index_image_analyse < len(images_a_analyser)-1 :
        bouton_precedente.configure(state='normal', style='Black.TButton')
        index_image_analyse += 1
        ca.delete('all')
        
        if MODE == 'Pre-analyse':
            img = images_a_analyser[index_image_analyse]
            ca.photo = Preparer_image(img, ca_taille[0], ca_taille[1])
            ca.create_image(0, 0, image=ca.photo, anchor='nw')

        if MODE == 'Post-analyse':
            img = images_analysees[index_image_analyse]
            img.thumbnail((ca_taille[0], ca_taille[1]))
            ca.photo_analysee = ImageTk.PhotoImage(image=img)
            ca.create_image(0, 0, image=ca.photo_analysee, anchor='nw')
            ligne = 31
            for classe in liste_classes[index_image_analyse]:
                txt_classes[ligne-31].configure(text=str(classe[1])+' soit '+
                                                    str(round(classe[1]/liste_nb_vignettes[index_image_analyse]*100,2))+' %')
                ligne += 1
        
        nom_img_analyse.configure(text=images_a_analyser[index_image_analyse].split('/')[-1])
    
    if index_image_analyse == len(images_a_analyser)-1:
        bouton_suivante.configure(state='disabled')

#--------------------------------------------------------------------------------------------------------------------------------
# MODE ANALYSE : Execution du CNN
#--------------------------------------------------------------------------------------------------------------------------------
def Mode_analyse_execution():
    bouton_precedente.configure(state='disabled')
    bouton_suivante.configure(state='disabled')
    bouton_lancer_analyse.configure(state='disabled')

    etat_analyse = Ajouter_texte(Analyse, "Analyse en cours ", 0, 95, 1, 'ew')
    barre = Progressbar(Analyse, style='Blue.Horizontal.TProgressbar', length=lecran/2, mode='determinate', 
                        maximum=len(images_a_analyser)+10**-10)
    barre.grid(column=1, row=95, columnspan=4, stick='we')
    barre.update()

    global images_analysees, liste_classes, liste_nb_vignettes
    images_analysees = []
    liste_classes = []
    liste_nb_vignettes = []

    for img in images_a_analyser:

        (image_analysee, classes, nb_vignettes) = Detection.Predire(img)
        images_analysees.append(image_analysee)
        liste_classes.append(classes)
        liste_nb_vignettes.append(nb_vignettes)
        
        barre.step(1)
        barre.update()
    
    etat_analyse.configure(text="Analyse terminée")

    global MODE
    MODE = 'Post-analyse'
    Enregistrer_image()

    ligne = 11
    for classe in liste_classes[0]:
        Ajouter_texte(Analyse, classe[0]['classe']+' : ', 5, ligne, 1, 'w')
        ligne += 1
    ligne = 31
    for classe in liste_classes[0]:
        Ajouter_texte(Analyse, classe[0]['classe']+' : ', 5, ligne, 1, 'w')
        ligne += 1

    meta_donnees = []
    for i in range(len(images_analysees)):
        donnees = []
        for classe in liste_classes[i]:
            donnees.append(classe[1])
        meta_donnees.append(donnees)
    
    sommes = []
    for i in range(len(meta_donnees[0])):
        somme = 0
        for donnee in meta_donnees:
            somme += donnee[i]
        sommes.append(somme)

    somme_vignettes = 0
    for i in range(len(liste_nb_vignettes)):
        somme_vignettes += liste_nb_vignettes[i]

    sommes_pourcentage = [None]*len(sommes)
    for i in range(len(sommes)):
        sommes_pourcentage[i] = round(sommes[i]/somme_vignettes*100,2)

    ligne = 11
    for classe in liste_classes[0]:
        Ajouter_texte(Analyse, str(sommes[ligne-11])+' soit '+str(sommes_pourcentage[ligne-11])+' %', 6, ligne, 1, 'w')
        ligne += 1

    global txt_classes
    txt_classes = []
    ligne = 31
    for classe in liste_classes[0]:
        t = Ajouter_texte(Analyse, str(classe[1])+' soit '+str(round(classe[1]/liste_nb_vignettes[0]*100,2))+' %', 6, ligne, 1,
                         'w')
        txt_classes.append(t)
        ligne += 1
    
    if index_image_analyse != 0:
        bouton_precedente.configure(state='normal', style='Black.TButton')
    if index_image_analyse != len(images_analysees)-1:
        bouton_suivante.configure(state='normal', style='Black.TButton')

    # On remplace l'image choisie par l'image analysée
    ca.delete("all")
    image = images_analysees[index_image_analyse]
    image.thumbnail((ca_taille[0], ca_taille[1]))
    ca.photo_analysee = ImageTk.PhotoImage(image=image)
    ca.create_image(0, 0, image=ca.photo_analysee, anchor='nw')

#--------------------------------------------------------------------------------------------------------------------------------
# MODE ANALYSE : Quitter le mode analyse
#--------------------------------------------------------------------------------------------------------------------------------
def Fermeture_analyse():
    Analyse.destroy()
    bouton_analyse.configure(state='normal')
    bouton_entrainement.configure(state='normal')
    bouton_quitter.configure(state='normal')

#################################################################################################################################
# Main
#################################################################################################################################
Racine = Tk()
Racine.option_add('*tearOff', FALSE)
Racine.withdraw()
lecran = Racine.winfo_screenwidth()
hecran = Racine.winfo_screenheight()
    
# Configuration des styles des widgets utilisés
s = Style()
s.theme_use('clam')

s.configure('Blue.Horizontal.TProgressbar', foreground='black', background='deep sky blue')
s.configure('Green.TButton', foreground='green', focuscolor='None')
s.configure('Red.TButton', foreground='red', focuscolor='None')
s.configure('Magenta.TButton', foreground='magenta', focuscolor='None')
s.configure('Black.TButton', foreground='black', focuscolor='None')
s.configure('Grey.TButton', foreground='grey', focuscolor='None')

s.configure('BackBlue.TButton', background='blue')
s.map('BackBlue.TButton', background=[('pressed', '!focus', 'blue')])
s.configure('BackRed.TButton', background='red')
s.map('BackRed.TButton', background=[('pressed', '!focus', 'red')])
s.configure('BackGreen.TButton', background='green')
s.map('BackGreen.TButton', background=[('pressed', '!focus', 'green')])
s.configure('BackWhite.TButton', background='white')
s.map('BackWhite.TButton', background=[('pressed', '!focus', 'white')])
s.configure('BackBlack.TButton', background='black')
s.map('BackBlack.TButton', background=[('pressed', '!focus', 'black')])
s.configure('BackYellow.TButton', background='yellow')
s.map('BackYellow.TButton', background=[('pressed', '!focus', 'yellow')])
s.configure('BackPink.TButton', background='pink')
s.map('BackPink.TButton', background=[('pressed', '!focus', 'pink')])
s.configure('BackCyan.TButton', background='cyan')
s.map('BackCyan.TButton', background=[('pressed', '!focus', 'cyan')])
s.configure('BackOrange.TButton', background='orange')
s.map('BackOrange.TButton', background=[('pressed', '!focus', 'orange')])
s.configure('BackMagenta.TButton', background='magenta')
s.map('BackMagenta.TButton', background=[('pressed', '!focus', 'magenta')])

S = Font(font='TkDefaultFont')
S.configure(underline=True)
SG = Font(font='TkDefaultFont')
SG.configure(underline=True, weight='bold')

# Création de la 1ère fenêtre
Definir_geometrie(Racine, 'Morpheus', 3.5/10*lecran, 2/10*hecran, 4, 4)
Ajouter_texte(Racine, "Détection d'organismes", 0, 0, 4, 'ew').configure(font=SG)
bouton_entrainement = Ajouter_bouton(Racine, 'Mode entraînement', 'Magenta.TButton', Mode_entrainement_accueil, 0, 3, 1)
bouton_analyse = Ajouter_bouton(Racine, 'Mode analyse', 'Green.TButton', Mode_analyse_accueil, 1, 3, 1)
bouton_quitter = Ajouter_bouton(Racine, 'Quitter', 'Red.TButton', Racine.destroy, 3, 3, 1)
bouton_analyse.configure(state='disabled')
bouton_entrainement.configure(state='disabled')

e = Entry(Racine, show='*')
e.grid(column=1, row=1, columnspan=1)

texte_mdp = Ajouter_texte(Racine, "Rentrer le mot de passe" +"\n"+ "pour vous connecter : ", 0, 1, 1,'ew')
bouton_se_connecter = Ajouter_bouton(Racine, "Se connecter", 'Green.TButton', lambda : Se_Connecter(e, login), 2, 1, 1)
login = Ajouter_texte(Racine, "", 3, 1, 1, None)

Racine.mainloop()