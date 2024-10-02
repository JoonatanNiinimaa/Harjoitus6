import tkinter as tk
from tkinter import PhotoImage
import numpy as np
import threading
import random
import time
import winsound  

root = tk.Tk()
root.title("Ernesti ja Kernestin uima-allas")
root.geometry("1200x800")

# Kuvien lataaminen ja koon muokkaaminen
try:
    saari_img = PhotoImage(file="saari.png")
    ernesti_img = PhotoImage(file="erne.png").subsample(4, 4)
    kernesti_img = PhotoImage(file="kerne.png").subsample(4, 4)
    viidakko_img = PhotoImage(file="viidakko.png").subsample(7, 7)  # Pienennetään viidakko.png kuvaa
    monkey_img = PhotoImage(file="monkey.png").subsample(5, 5)  # Apinan kuva, pienennetään hieman
except Exception as e:
    print(f"Virhe kuvien lataamisessa: {e}")
    root.destroy()
    exit()

# Paikat ikkunassa
canvas = tk.Canvas(root, width=1200, height=800)
canvas.pack()

# Piirretään saaren kuva
canvas.create_image(600, 400, image=saari_img)

# Uima-allas (muutettu väri kuvaamaan tyhjää allasta)
uima_allas_x1 = 450  # X-koordinaatti siirretty vasemmalle
uima_allas_y1 = 250  # Y-koordinaatti siirretty alemmaksi
uima_allas_x2 = uima_allas_x1 + 300  # 300 pikseliä leveä allas
uima_allas_y2 = uima_allas_y1 + 150  # 150 pikseliä korkea allas
canvas.create_rectangle(uima_allas_x1, uima_allas_y1, uima_allas_x2, uima_allas_y2, fill="sandy brown", outline="brown")  # Tyhjä allas beige

# Luodaan uima-allas matriisina (20x60, aluksi kaikki arvot ovat nollia)
allas_matriisi = np.zeros((20, 60))

# Ojat matriiseina (Ernestin ja Kernestin ojat, 100x1, aluksi täynnä hiekkaa eli arvo 1)
ernestin_oja_matriisi = np.ones((100, 1))  # Ernestin oja
kernestin_oja_matriisi = np.ones((100, 1))  # Kernestin oja

# Ernestin oja (hiekan värinen, kuvaamaan hiekkaa ojassa)
ernest_ojan_x1 = uima_allas_x1  # Oja alkaa uima-altaan vasemmasta reunasta
ernest_ojan_y1 = uima_allas_y1  # Oja alkaa uima-altaan yläreunasta
ernest_ojan_x2 = ernest_ojan_x1  # Oja jatkuu suoraan ylös
ernest_ojan_y2 = ernest_ojan_y1 - 100  # Oja on 100 pikseliä pitkä ja menee ylös
canvas.create_line(ernest_ojan_x1, ernest_ojan_y1, ernest_ojan_x2, ernest_ojan_y2, fill="sandy brown", width=2)

# Kernestin oja (myös hiekan värinen)
kernest_ojan_x1 = uima_allas_x2  # Oja alkaa uima-altaan oikeasta reunasta
kernest_ojan_y1 = uima_allas_y1  # Oja alkaa uima-altaan yläreunasta
kernest_ojan_x2 = kernest_ojan_x1  # Oja jatkuu suoraan ylös
kernest_ojan_y2 = kernest_ojan_y1 - 100  # Oja on 100 pikseliä pitkä ja menee ylös
canvas.create_line(kernest_ojan_x1, kernest_ojan_y1, kernest_ojan_x2, kernest_ojan_y2, fill="sandy brown", width=2)

ojat = [(ernest_ojan_x1, ernest_ojan_y1 - 100), (kernest_ojan_x1, kernest_ojan_y1 - 100)]

# Lisätään metsäalueet saarelle kolmessa kohtaa käyttäen viidakko.png kuvaa
metsan_paikat = [(230, 250), (900, 300), (800, 500)]  # Sijainnit metsäalueille
for (x, y) in metsan_paikat:
    canvas.create_image(x, y, image=viidakko_img)

# Ernestin ja Kernestin paikat (säilytetään ennallaan)
ernesti_pos = (500, 450)
kernesti_pos = (700, 450)
ernesti = canvas.create_image(*ernesti_pos, image=ernesti_img)
kernesti = canvas.create_image(*kernesti_pos, image=kernesti_img)

# Apinat metsään
apinat = []
apina_lkm = 5  # Määrä apinoita, voi muuttaa

for i in range(apina_lkm):
    metsa_x, metsa_y = random.choice(metsan_paikat)  # Valitaan satunnaisesti metsäalue
    apinan_pos = (metsa_x + random.randint(-50, 50), metsa_y + random.randint(-50, 50))  # Pieni satunnaisuus sijaintiin
    apina = canvas.create_image(*apinan_pos, image=monkey_img)
    apinat.append({'image': apina, 'has_shovel': False, 'ojalla': False})  # Apinan kuva ja lapion tila

# Liikuttaminen kohti kohdetta
def liiku_objekti(objekti, kohde_x, kohde_y):
    while True:  # Jatka liikuttamista kunnes saavutetaan kohde
        obj_x, obj_y = canvas.coords(objekti)  # Nykyinen sijainti
        if abs(obj_x - kohde_x) < 1 and abs(obj_y - kohde_y) < 1:
            canvas.coords(objekti, kohde_x, kohde_y)  # Varmista, että saavutetaan tarkka kohde
            break  # Lopeta liikkuminen, jos olemme riittävän lähellä
        uusi_x = obj_x + (kohde_x - obj_x) / 10  # Muuta divisoria suuremmaksi nopeammaksi liikkeeksi
        uusi_y = obj_y + (kohde_y - obj_y) / 10  # Muuta divisoria suuremmaksi nopeammaksi liikkeeksi
        canvas.coords(objekti, uusi_x, uusi_y)
        time.sleep(0.02)  # Vähennetään odotusaikaa nopeammaksi liikkeeksi

def ernest_opastaa_apinaa():
    if apinat:  # Jos on joutilaita apinoita
        # Etsi lähin apina, joka ei ole ojalla
        apina_distances = []
        ernest_x, ernest_y = canvas.coords(ernesti)  # Ernestin sijainti
        for apina in apinat:
            if not apina['ojalla']:  # Tarkistetaan, ettei apina ole ojalla
                apina_x, apina_y = canvas.coords(apina['image'])
                distance = ((ernest_x - apina_x) ** 2 + (ernest_y - apina_y) ** 2) ** 0.5
                apina_distances.append((distance, apina))

        if not apina_distances:
            print("Kaikki apinat ovat jo ojalla!")
            return
        
        # Lajittele etäisyyksien mukaan ja ota lähin apina
        apina_distances.sort(key=lambda x: x[0])
        closest_apina = apina_distances[0][1]

        # Siirrä Ernesti lähimmän apinan luo
        apina_image = closest_apina['image']
        apina_x, apina_y = canvas.coords(apina_image)  # Apinan sijainti
        threading.Thread(target=liiku_objekti, args=(ernesti, apina_x, apina_y)).start()  # Ernesti liikkuu apinan luo

        # Kun Ernesti on saapunut apinalle, anna lapio
        root.after(1000, lambda: anna_lapio(closest_apina, apina_image))

# Lista käytettävistä y-koordinaateista
kaytetyt_y_koordinaatit = []

def anna_lapio(apina, apina_image):
    # Anna apinalle lapio
    apina['has_shovel'] = True
    print("Apina on saanut lapion:", apina)

    # Merkitse apina ojalla olevan
    apina['ojalla'] = True

    # Määritä satunnainen y-koordinaatti, joka ei ole käytössä
    uusi_x = ernest_ojan_x1  # x-koordinaatti pysyy vakiona ojan kohdalla
    uusi_y = ernest_ojan_y1 - random.randint(10, 90)  # Satunnainen y-koordinaatti ojan alueella

    # Varmista, että y-koordinaatti ei ole jo käytössä
    while uusi_y in kaytetyt_y_koordinaatit:
        uusi_y = ernest_ojan_y1 - random.randint(10, 90)  # Etsi uusi satunnainen y-koordinaatti

    # Lisää uusi y-koordinaatti käytetyksi
    kaytetyt_y_koordinaatit.append(uusi_y)

    # Siirrä apina ojalle
    threading.Thread(target=liiku_objekti, args=(apina_image, uusi_x, uusi_y)).start()  # Apina liikkuu ojaan


# Käynnistetään käyttöliittymä
opasta_apinaa_button = tk.Button(root, text="Hae apina ja anna lapio", command=ernest_opastaa_apinaa)
opasta_apinaa_button.pack(pady=20)  # Lisätään painike ikkunaan

root.mainloop()

# Tulostetaan matriisit tarkistusta varten
print("Uima-altaan matriisi (tyhjä allas):")
print(allas_matriisi)

print("\nErnestin ojan matriisi (täynnä hiekkaa, arvo 1):")
print(ernestin_oja_matriisi)

print("\nKernestin ojan matriisi (täynnä hiekkaa, arvo 1):")
print(kernestin_oja_matriisi)
