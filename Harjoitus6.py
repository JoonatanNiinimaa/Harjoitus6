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
apina_lkm = 10  # Määrä apinoita, voi muuttaa

for i in range(apina_lkm):
    metsa_x, metsa_y = random.choice(metsan_paikat)  # Valitaan satunnaisesti metsäalue
    apinan_pos = (metsa_x + random.randint(-50, 50), metsa_y + random.randint(-50, 50))  # Pieni satunnaisuus sijaintiin
    apina = canvas.create_image(*apinan_pos, image=monkey_img)
    apinat.append({'image': apina, 'has_shovel': False, 'ojalla': False, 'kaivamis_index': None})  # Apinan kuva, lapion tila ja kaivamisen indeksi

# Liikuttaminen kohti kohdetta
def liiku_objekti(objekti, kohde_x, kohde_y):
    while True:  # Jatka liikuttamista kunnes saavutaan kohde
        obj_x, obj_y = canvas.coords(objekti)  # Nykyinen sijainti
        if abs(obj_x - kohde_x) < 1 and abs(obj_y - kohde_y) < 1:
            canvas.coords(objekti, kohde_x, kohde_y)  # Varmista, että saavutaan tarkka kohde
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
        root.after(1000, lambda: e_anna_lapio(closest_apina, apina_image))

def kernest_opastaa_apinaa():
    if apinat:  # Jos on joutilaita apinoita
        # Etsi lähin apina, joka ei ole ojalla
        apina_distances = []
        kernest_x, kernest_y = canvas.coords(kernesti)  # Ernestin sijainti
        for apina in apinat:
            if not apina['ojalla']:  # Tarkistetaan, ettei apina ole ojalla
                apina_x, apina_y = canvas.coords(apina['image'])
                distance = ((kernest_x - apina_x) ** 2 + (kernest_y - apina_y) ** 2) ** 0.5
                apina_distances.append((distance, apina))

        if not apina_distances:
            print("Kaikki apinat ovat jo ojalla!")
            return
        
        # Lajittele etäisyyksien mukaan ja ota lähin apina
        apina_distances.sort(key=lambda x: x[0])
        closest_apina = apina_distances[0][1]

        # Siirrä Kernesti lähimmän apinan luo
        apina_image = closest_apina['image']
        apina_x, apina_y = canvas.coords(apina_image)  # Apinan sijainti
        threading.Thread(target=liiku_objekti, args=(kernesti, apina_x, apina_y)).start()  # Kernesti liikkuu apinan luo

        # Kun Kernesti on saapunut apinalle, anna lapio
        root.after(1000, lambda: k_anna_lapio(closest_apina, apina_image))

# Lisätään uusi nappi kaivamisen aloittamiseksi
def kaivaa(apina):
    oja_index = apina['kaivamis_index']  # Ota apinan nykyinen kaivamisindeksi
    if oja_index is not None and oja_index < len(ernestin_oja_matriisi):  # Kunnes kaivamme koko ojan
        # Varmista, että oja on vielä "hiekkaa" (arvo 1)
        if ernestin_oja_matriisi[oja_index][0] == 1:
            # Muutetaan ojan arvo nollaksi
            ernestin_oja_matriisi[oja_index][0] = 0

            # Soita ääni
            winsound.Beep(1000, 100)  # Esimerkiksi 1000 Hz 100 ms
            print(f"Kaivettu ojan kohdasta: {oja_index}")

            # Siirrä apina ojan varrella
            uusi_y = ernest_ojan_y1 - (oja_index * (100 / len(ernestin_oja_matriisi)))  # Skaalataan y-koordinaatti
            canvas.coords(apina['image'], ernest_ojan_x1, uusi_y)  # Siirretään apina ojalle

            # Vähennä indeksiä
            apina['kaivamis_index'] += 1  # Lisää indeksiä, että seuraava askel ylös
            
            # Ajan laskeminen väsymisen mukaan
            kaivamis_aika = 1 * (2 ** (apina['kaivamis_index'] - 1))  # Jokaisen seuraavan metrin kaivamiseen menee kaksinkertainen aika
            
            # Rajaa kaivamis_aika maksimiin, esimerkiksi 30 sekuntiin
            if kaivamis_aika > 30:
                kaivamis_aika = 30

            # Odota apinan kaivamisajan verran käyttäen after-funktiota
            root.after(int(kaivamis_aika * 1000), lambda: kaivaa(apina))  # Kutsu uudelleen kaivamista
        else:
            print("Oja on jo kaivettu, ei voida kaivaa.")
    else:
        print("Kaivaminen valmis.")

def e_anna_lapio(apina, apina_image):
    # Anna apinalle lapio
    apina['has_shovel'] = True
    print("Apina on saanut lapion:", apina)

    # Merkitse apina ojalla olevan ja tallenna indeksi
    apina['ojalla'] = True  # Apina on nyt ojalla
    apina['kaivamis_index'] = random.randint(0, len(ernestin_oja_matriisi) - 1)  # Aloita kaivaminen satunnaisesta kohdasta

    # Siirrä apina ojan kohdalle
    uusi_x = ernest_ojan_x1  # X-koordinaatti pysyy vakiona ojan kohdalla
    uusi_y = ernest_ojan_y1 - (apina['kaivamis_index'] * (100 / len(ernestin_oja_matriisi)))  # Apinan y-koordinaatti ojan alueella

    threading.Thread(target=liiku_objekti, args=(apina_image, uusi_x, uusi_y)).start()  # Siirrä apina ojalle

# Lisätään kaivamispainike
def k_anna_lapio(apina, apina_image):
    # Anna apinalle lapio
    apina['has_shovel'] = True
    print("Apina on saanut lapion:", apina)

    # Merkitse apina ojalla olevan ja tallenna indeksi
    apina['ojalla'] = True  # Apina on nyt ojalla
    apina['kaivamis_index'] = random.randint(0, len(kernestin_oja_matriisi) - 1)  # Aloita kaivaminen satunnaisesta kohdasta

    # Siirrä apina ojan kohdalle
    uusi_x = kernest_ojan_x1  # X-koordinaatti pysyy vakiona ojan kohdalla
    uusi_y = kernest_ojan_y1 - (apina['kaivamis_index'] * (100 / len(kernestin_oja_matriisi)))  # Apinan y-koordinaatti ojan alueella

    threading.Thread(target=liiku_objekti, args=(apina_image, uusi_x, uusi_y)).start()  # Siirrä apina ojalle

# Aloita kaivaminen
def e_aloita_kaivaminen():
    for apina in apinat:
        if apina['has_shovel'] and apina['ojalla']:  # Tarkista, onko apinalla lapio ja että se on ojalla
            apina['kaivamis_index'] = apina['kaivamis_index']  # Aloita kaivaminen ajankohtaisesta kohdasta
            kaivaa(apina)  # Aloita kaivaminen
        else:
            print("Ei yhtään apinaa, jolla on lapio.")

def k_aloita_kaivaminen():
    for apina in apinat:
        if apina['has_shovel'] and apina['ojalla']:  # Tarkista, onko apinalla lapio ja että se on ojalla
            apina['kaivamis_index'] = apina['kaivamis_index']  # Aloita kaivaminen ajankohtaisesta kohdasta
            kaivaa(apina)  # Aloita kaivaminen
        else:
            print("Ei yhtään apinaa, jolla on lapio.")

# Tarkista ojalla olevat apinat
def tarkista_ojalla_olevat_apinat():
    ojalla_olevat_apinat = [apina for apina in apinat if apina['ojalla']]
    if ojalla_olevat_apinat:
        print("Ojalla olevat apinat:")
        for i, apina in enumerate(ojalla_olevat_apinat):
            print(f"Apina {i + 1}: {apina}")
    else:
        print("Ei yhtään apinaa ojalla.")

# Lisää nappi tarkistaakseen ojalla olevat apinat
tarkista_button = tk.Button(root, text="Tarkista ojalla olevat apinat", command=tarkista_ojalla_olevat_apinat)
tarkista_button.pack(pady=20)  # Lisätään painike ikkunaan

# Ernesti opastaa apinaa
opasta_apinaa_button = tk.Button(root, text="Ernesti hakee apinan ja antaa lapio", command=ernest_opastaa_apinaa)
opasta_apinaa_button.pack(pady=20)  # Lisätään painike ikkunaan
# Lisätään kaivamispainike
kaiva_button = tk.Button(root, text="Aloita Ernestin ojan kaivaminen", command=lambda: e_aloita_kaivaminen())
kaiva_button.pack(pady=20)  # Lisätään kaivamispainike

# Kernesti opastaa apinaa
opasta_apinaa_button = tk.Button(root, text="Kernesti hakee apinan ja antaa lapio", command=kernest_opastaa_apinaa)
opasta_apinaa_button.pack(pady=20)  # Lisätään painike ikkunaan
# Lisätään kaivamispainike
kaiva_button = tk.Button(root, text="Aloita Kernestin ojan kaivaminen", command=lambda: k_aloita_kaivaminen())
kaiva_button.pack(pady=20)  # Lisätään kaivamispainike

root.mainloop()

# Tulostetaan matriisit tarkistusta varten
print("Uima-altaan matriisi (tyhjä allas):")
print(allas_matriisi)

print("\nErnestin ojan matriisi (täynnä hiekkaa, arvo 1):")
print(ernestin_oja_matriisi)

print("\nKernestin ojan matriisi (täynnä hiekkaa, arvo 1):")
print(kernestin_oja_matriisi)
