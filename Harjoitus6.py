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
    saari_img = PhotoImage(file="saari.png").subsample(2,2)
    ernesti_img = PhotoImage(file="erne.png").subsample(6, 6)
    kernesti_img = PhotoImage(file="kerne.png").subsample(6, 6)
    viidakko_img = PhotoImage(file="viidakko.png").subsample(12, 12)  # Pienennetään viidakko.png kuvaa
    monkey_img = PhotoImage(file="monkey.png").subsample(6, 6)  # Apinan kuva, pienennetään hieman
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
uima_allas_x1 = 575  # X-koordinaatti siirretty vasemmalle
uima_allas_y1 = 375  # Y-koordinaatti siirretty alemmaksi
uima_allas_x2 = uima_allas_x1 + 60  # 60 pikseliä leveä allas
uima_allas_y2 = uima_allas_y1 + 20  # 20 pikseliä korkea allas
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

def tayta_ja_nollaa_oja():
    global apinat  # Jos käytetään globaalia apina-listaa
    
    # Nollataan ojamatriisit
    for i in range(len(ernestin_oja_matriisi)):
        ernestin_oja_matriisi[i][0] = 1  # Asetetaan arvoksi 1, eli alkuperäinen hiekkakerros

    for i in range(len(kernestin_oja_matriisi)):
        kernestin_oja_matriisi[i][0] = 1  # Sama kernestin ojaan

    # Poistetaan apinat ojalta ja nollataan niiden kaivamisindeksit
    for apina in apinat:
        # Poistetaan apinan kuva ensin
        if 'image' in apina and apina['image'] is not None and apina['ojalla'] == True:
            canvas.delete(apina['image'])  # Poistetaan vain tämän apinan kuva
            apina['image'] = None  # Nollataan kuvan viittaus
        
        # Asetetaan apina pois ojalta vasta kuvan poistamisen jälkeen
        apina['ojalla'] = False
        apina['kaivamis_index'] = 0
    paivita_oja_visuals()

    print("Ojien arvot on nollattu ja apinat poistettu ojalta.")

def paivita_oja_visuals():
    """Päivitä ojien visuaalinen näyttö nollauksen jälkeen."""
    for i in range(len(ernestin_oja_matriisi)):
        # Laske y-koordinaatti
        kaivetun_osan_y = ernest_ojan_y1 - (i * (100 / len(ernestin_oja_matriisi)))
        # Asetetaan alkuperäinen hiekan väri
        current_color = hiekan_vari(1)  # Hiekan väri syvyydellä 1
        canvas.create_rectangle(ernest_ojan_x1, kaivetun_osan_y, ernest_ojan_x1 + 3, kaivetun_osan_y + (100 / len(ernestin_oja_matriisi)), fill=current_color, outline="")

    for i in range(len(kernestin_oja_matriisi)):
        kaivetun_osan_y = kernest_ojan_y1 - (i * (100 / len(kernestin_oja_matriisi)))
        current_color = hiekan_vari(1)
        canvas.create_rectangle(kernest_ojan_x1, kaivetun_osan_y, kernest_ojan_x1 + 3, kaivetun_osan_y + (100 / len(kernestin_oja_matriisi)), fill=current_color, outline="")

    print("Oja on päivitetty visuaalisesti.")

def tarkista_uima_allas():
    while True:
        # Tarkista, onko molemmat ojat tyhjentyneet
        oja1_kaivettu = all(section[0] <= 0 for section in ernestin_oja_matriisi)
        oja2_kaivettu = all(section[0] <= 0 for section in kernestin_oja_matriisi)

        # Tarkista ja muuta Ernestin oja siniseksi, jos kaikki sen osat ovat tyhjentyneet
        if oja1_kaivettu:
            print("Ernestin oja muuttuu siniseksi, koska kaikki osat ovat tyhjentyneet.")
            canvas.create_line(ernest_ojan_x1, ernest_ojan_y1, ernest_ojan_x2, ernest_ojan_y2, fill="blue")

        # Tarkista ja muuta Kernestin oja siniseksi, jos kaikki sen osat ovat tyhjentyneet
        if oja2_kaivettu:
            print("Kernestin oja muuttuu siniseksi, koska kaikki osat ovat tyhjentyneet.")
            canvas.create_line(kernest_ojan_x1, kernest_ojan_y1, kernest_ojan_x2, kernest_ojan_y2, fill="blue")
       
        # Muuta uima-allasta siniseksi, jos molemmat ojat ovat tyhjät
        if oja1_kaivettu and oja2_kaivettu:
            print("Uima-allas muuttuu siniseksi, koska molemmat ojat ovat tyhjät.")
            canvas.create_rectangle(uima_allas_x1, uima_allas_y1, uima_allas_x2, uima_allas_y2, fill="blue")
            break  # Lopeta silmukka, kun allas on muutettu
        time.sleep(1)  # Odota hetki ennen seuraavaa tarkistusta

# Luodaan ja käynnistetään säie uima-allaan tarkistamiseen
uima_allas_tarkistus_säie = threading.Thread(target=tarkista_uima_allas)
uima_allas_tarkistus_säie.start()

# Lisätään metsäalueet saarelle kolmessa kohtaa käyttäen viidakko.png kuvaa
metsan_paikat = [(425, 325), (775, 300), (750, 420)]  # Sijainnit metsäalueille
for (x, y) in metsan_paikat:
    canvas.create_image(x, y, image=viidakko_img)

# Ernestin ja Kernestin paikat (säilytetään ennallaan)
ernesti_pos = (550, 440)
kernesti_pos = (650, 440)
ernesti = canvas.create_image(*ernesti_pos, image=ernesti_img)
kernesti = canvas.create_image(*kernesti_pos, image=kernesti_img)

# Apinat metsään
apinat = []
apina_lkm = 100  # Määrä apinoita, voi muuttaa

for i in range(apina_lkm):
    metsa_x, metsa_y = random.choice(metsan_paikat)  # Valitaan satunnaisesti metsäalue
    apinan_pos = (metsa_x + random.randint(-50, 50), metsa_y + random.randint(-30, 30))  # Pieni satunnaisuus sijaintiin
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

def hiekan_vari(depth):
    if depth == 1:
        return "#D1A55D"  # Pinnallinen hiekkakerros
    elif depth == 0:
        return "#B5944D"  # Ensimmäinen kaivettu kerros
    elif depth == -1:
        return "#A07D3D"  
    elif depth == -2:
        return "#7B6A2B"  
    elif depth == -3:
        return "#6e5424"  
    else:
        return "#4D3B1A"  

def kaivaa(apina):
    if apina['ojalla']:
        if apina['has_shovel']:
            oja_matriisi = ernestin_oja_matriisi if apina['nimi'] == 'Ernesti' else kernestin_oja_matriisi
            oja_x1 = ernest_ojan_x1 if apina['nimi'] == 'Ernesti' else kernest_ojan_x1
            oja_y1 = ernest_ojan_y1 if apina['nimi'] == 'Ernesti' else kernest_ojan_y1

            oja_index = apina['kaivamis_index']  # Ota apinan nykyinen kaivamisindeksi

            if oja_index is not None and oja_index < len(oja_matriisi):
                # Tarkista syvyys
                current_depth = oja_matriisi[oja_index][0]

                if current_depth > -1:  # Voidaan kaivaa, jos syvyys on suurempi tai yhtä suuri kuin -1
                    # Oja on "hiekkaa", apina voi kaivaa
                    oja_matriisi[oja_index][0] -= 1  # Vähennetään arvoa, jotta se merkitsee kaivettua
                    print(f"{apina['nimi']}n apina kaivoi ojan kohdasta: {oja_index}")

                    # Muuta hiekan väriä syvyyden mukaan
                    depth = oja_matriisi[oja_index][0]  # Käytetään matriisin arvoa syvyyden määrittämiseen
                    kaivetun_osan_y = oja_y1 - (oja_index * (100 / len(oja_matriisi)))  # Laske y-koordinaatti
                else:
                    # Oja on jo kaivettu tai syvyys on negatiivinen
                    print(f"{apina['nimi']} ei voi kaivaa enää, oja on jo valmis kohdassa {oja_index}.")

                # Vähennä indeksiä
                apina['kaivamis_index'] += 1

                # Ajan laskeminen
                kaivamis_aika = 1 * (2 ** (apina['kaivamis_index'] - 1))
                if kaivamis_aika > 30:
                    kaivamis_aika = 30

                # Tarkista, onko kaivaminen valmis
                if apina['kaivamis_index'] >= len(oja_matriisi):
                    # Tarkista, onko koko oja kaivettu (kaikki 0 tai pienempiä)
                    if all(section[0] <= 0 for section in oja_matriisi):
                        # Muuta koko oja siniseksi, kun kaikki on kaivettu
                        for i in range(len(oja_matriisi)):
                            kaivetun_osan_y = oja_y1 - (i * (100 / len(oja_matriisi)))  # Laske y-koordinaatti
                            canvas.create_rectangle(oja_x1, kaivetun_osan_y, oja_x1 + 20, kaivetun_osan_y + (100 / len(oja_matriisi)), fill="blue", outline="")
                        print(f"{apina['nimi']} on valmis kaivamisessa. Kaikki on kaivettu!")
                    else:
                        print(f"{apina['nimi']} on valmis kaivamisessa, mutta kaikki ojan osat eivät ole kaivettu vielä.")

                else:
                    # Odota kaivamisajan verran käyttäen after-funktiota
                    root.after(int(kaivamis_aika * 1000), lambda: kaivaa(apina))  # Kutsu uudelleen kaivamista

            else:
                print(f"{apina['nimi']} on valmis kaivamisessa.")

def e_anna_lapio(apina, apina_image):
    # Anna apinalle lapio
    apina['has_shovel'] = True
    apina['nimi'] = 'Ernesti'  # Aseta apinan nimi
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
    apina['nimi'] = 'Kernesti'  # Aseta apinan nimi

    # Merkitse apina ojalla olevan ja tallenna indeksi
    apina['ojalla'] = True  # Apina on nyt ojalla
    apina['kaivamis_index'] = random.randint(0, len(kernestin_oja_matriisi) - 1)  # Aloita kaivaminen satunnaisesta kohdasta

    # Siirrä apina ojan kohdalle
    uusi_x = kernest_ojan_x1  # X-koordinaatti pysyy vakiona ojan kohdalla
    uusi_y = kernest_ojan_y1 - (apina['kaivamis_index'] * (100 / len(kernestin_oja_matriisi)))  # Apinan y-koordinaatti ojan alueella

    threading.Thread(target=liiku_objekti, args=(apina_image, uusi_x, uusi_y)).start()  # Siirrä apina ojalle

# Aloita kaivaminen
def e_aloita_kaivaminen():
    kaivettavat_apinat = []  # Lista kaivettavista apinoista
    for apina in apinat:
        if apina['has_shovel'] and apina['ojalla'] and apina['nimi'] == 'Ernesti':
            kaivettavat_apinat.append(apina)  # Lisää kaivettavat apinat listaan

    if kaivettavat_apinat:
        for apina in kaivettavat_apinat:
            apina['kaivamis_index'] = apina['kaivamis_index']  # Aloita kaivaminen ajankohtaisesta kohdasta
            kaivaa(apina)  # Aloita kaivaminen jokaiselle apinalle
    else:
        print("Ei yhtään Ernestin apinaa, jolla on lapio.")

def k_aloita_kaivaminen():
    kaivettavat_apinat = []  # Lista kaivettavista apinoista
    for apina in apinat:
        if apina['has_shovel'] and apina['ojalla'] and apina['nimi'] == 'Kernesti':
            kaivettavat_apinat.append(apina)  # Lisää kaivettavat apinat listaan

    if kaivettavat_apinat:
        for apina in kaivettavat_apinat:
            apina['kaivamis_index'] = apina['kaivamis_index']  # Aloita kaivaminen ajankohtaisesta kohdasta
            kaivaa(apina)  # Aloita kaivaminen jokaiselle apinalle
    else:
        print("Ei yhtään Ernestin apinaa, jolla on lapio.")

def e_aloita_fiksu_kaivaminen():
    """Aloittaa fiksun kaivamislogiikan ja rajoittaa apinoiden määrän 10 apinaan."""
    kaivettavat_apinat = [apina for apina in apinat if not apina.get('has_shovel')]  # Suodata apinat, joilla ei ole lapioa

    # Ota vain 10 apinaa
    kaivettavat_apinat = kaivettavat_apinat[:10]  # Rajoita 10 apinaan

    # Anna kullekin apinalle lapio ja aloita kaivaminen sekunnin välein
    if kaivettavat_apinat:
        for i, apina in enumerate(kaivettavat_apinat):
            # Anna apinalle lapio
            e_anna_lapio(apina, apina['image'])
            # Käytetään apinan oikeaa instanssia lambda-funktiossa
            root.after(i * 1000, lambda apina=apina: e_sijoita_ja_aloita_kaivaminen(apina))
    else:
        print("Ei yhtään apinaa, jolla ei ole lapioa.")

def e_sijoita_ja_aloita_kaivaminen(apina):
    """Sijoittaa apinan ojan varrelle ja aloittaa kaivamisen."""
    # Etsi kaikki saatavilla olevat indeksi (arvo 1) ojan matriisista
    saatavilla_olevat = [indeksi for indeksi in range(len(ernestin_oja_matriisi)) if ernestin_oja_matriisi[indeksi][0] == 1]

    if saatavilla_olevat:
        # Valitse satunnainen indeksi saatavilla olevista
        indeksi = random.choice(saatavilla_olevat)

        # Sijoita apina ojan varrelle
        oja_x1 = ernest_ojan_x1
        oja_y1 = ernest_ojan_y1
        apina['kaivamis_index'] = indeksi  # Sijoitetaan apina ojan kohtaan "indeksi"
        
        # Määritä apinan sijainti ojan kohdalle
        uusi_x = oja_x1  # x-koordinaatti on sama ojan kohdalla
        uusi_y = oja_y1 - (indeksi * (100 / len(ernestin_oja_matriisi)))  # y-koordinaatti lasketaan indeksin mukaan
        
        # Siirrä apina oikeaan kohtaan
        threading.Thread(target=liiku_objekti, args=(apina['image'], uusi_x, uusi_y)).start()
        
        # Aloita kaivaminen
        kaivaa(apina)
        
        # Muutetaan ojan matriisin arvo 0:ksi, koska kaivaminen alkaa
        ernestin_oja_matriisi[indeksi][0] = 0

        # Siirrä seuraava apina 1 sekunnin kuluttua
        root.after(1000, lambda: e_sijoita_ja_aloita_kaivaminen(apina))  # Jatketaan seuraavaan satunnaiseen paikkaan
    else:
        piilota_apina(apina)  # Kutsu piilota_apina-funktiota

def k_aloita_fiksu_kaivaminen():
    """Aloittaa fiksun kaivamislogiikan ja rajoittaa apinoiden määrän 10 apinaan."""
    kaivettavat_apinat = [apina for apina in apinat if not apina.get('has_shovel')]  # Suodata apinat, joilla ei ole lapioa

    # Ota vain 10 apinaa
    kaivettavat_apinat = kaivettavat_apinat[:10]  # Rajoita 10 apinaan

    # Anna kullekin apinalle lapio ja aloita kaivaminen
    if kaivettavat_apinat:
        for i, apina in enumerate(kaivettavat_apinat):
            # Anna apinalle lapio
            k_anna_lapio(apina, apina['image'])
            # Käytetään apinan oikeaa instanssia lambda-funktiossa
            root.after(i * 1000, lambda apina=apina: k_sijoita_ja_aloita_kaivaminen(apina))
    else:
        print("Ei yhtään apinaa, jolla ei ole lapioa.")

def k_sijoita_ja_aloita_kaivaminen(apina):
    """Sijoittaa apinan ojan varrelle ja aloittaa kaivamisen."""
    # Etsi kaikki saatavilla olevat indeksi (arvo 1) ojan matriisista
    saatavilla_olevat = [indeksi for indeksi in range(len(kernestin_oja_matriisi)) if kernestin_oja_matriisi[indeksi][0] == 1]

    if saatavilla_olevat:
        # Valitse satunnainen indeksi saatavilla olevista
        indeksi = random.choice(saatavilla_olevat)

        # Sijoita apina ojan varrelle
        oja_x1 = kernest_ojan_x1
        oja_y1 = kernest_ojan_y1
        apina['kaivamis_index'] = indeksi  # Sijoitetaan apina ojan kohtaan "indeksi"
        
        # Määritä apinan sijainti ojan kohdalle
        uusi_x = oja_x1  # x-koordinaatti on sama ojan kohdalla
        uusi_y = oja_y1 - (indeksi * (100 / len(kernestin_oja_matriisi)))  # y-koordinaatti lasketaan indeksin mukaan
        
        # Siirrä apina oikeaan kohtaan
        threading.Thread(target=liiku_objekti, args=(apina['image'], uusi_x, uusi_y)).start()
        
        # Aloita kaivaminen
        kaivaa(apina)
        
        # Muutetaan ojan matriisin arvo 0:ksi, koska kaivaminen alkaa
        kernestin_oja_matriisi[indeksi][0] = 0

        # Siirrä seuraava apina 1 sekunnin kuluttua
        root.after(1000, lambda: k_sijoita_ja_aloita_kaivaminen(apina))  # Jatketaan seuraavaan satunnaiseen paikkaan
    else:
        piilota_apina(apina)  # Kutsu piilota_apina-funktiota

def piilota_apina(apina):
    """Piilottaa apinan canvasista."""
    if 'image' in apina and apina['image'] is not None:
        # Piilotetaan apinan kuva
        canvas.itemconfig(apina['image'], state='hidden')  # Tai vaihtoehtoisesti canvas.delete(apina['image'])
        apina['image'] = None  # Nollataan kuvan viittaus
        apina['ojalla'] = False  # Asetetaan apina pois ojalta
        apina['kaivamis_index'] = 0  # Nollataan kaivamisindeksi
        print(f"{apina['nimi']} on piilotettu ojalta.")

# Tarkista ojalla olevat apinat
def tarkista_ojalla_olevat_apinat():
    ojalla_olevat_apinat = [apina for apina in apinat if apina['ojalla']]
    if ojalla_olevat_apinat:
        print("Ojalla olevat apinat:")
        for i, apina in enumerate(ojalla_olevat_apinat):
            print(f"Apina {i + 1}: {apina}")
    else:
        print("Ei yhtään apinaa ojalla.")

def tarkista_ojamatriisi():
    """Tarkistaa ja palauttaa Ernestin ja Kernestin ojien arvot."""
    # Tarkista Ernestin ojan arvot
    print(ernestin_oja_matriisi)
    print(kernestin_oja_matriisi)

# Lisää nappi tarkistaakseen ojalla olevat apinat
tarkista_button = tk.Button(root, text="Tarkista ojalla olevat apinat", command=tarkista_ojalla_olevat_apinat)
canvas.create_window(600, 150, window=tarkista_button)

tarkista_ojamatriisi =tk.Button(root, text="Tarkista ojien arvot",command=tarkista_ojamatriisi)
canvas.create_window(600, 200, window=tarkista_ojamatriisi)

tayta_oja_button = tk.Button(root, text="Täytä ojat", command=tayta_ja_nollaa_oja)
canvas.create_window(600, 250, window=tayta_oja_button)

# Ernesti opastaa apinaa
e_opasta_apinaa_button = tk.Button(root, text="Ernesti hakee apinan ja antaa lapio", command=ernest_opastaa_apinaa)
canvas.create_window(350, 150, window=e_opasta_apinaa_button)

# Lisätään kaivamispainike
e_kaiva_button = tk.Button(root, text="Aloita Ernestin ojan kaivaminen", command=lambda: e_aloita_kaivaminen())
canvas.create_window(350, 200, window=e_kaiva_button)

# Ernestin Nappi fiksummalle kaivamiselle
e_fiksu_kaiva_button = tk.Button(root, text="Fiksu Ernestin ojan kaivaminen", command=lambda:e_aloita_fiksu_kaivaminen())
canvas.create_window(350, 250, window=e_fiksu_kaiva_button)

# Kernesti opastaa apinaa
k_opasta_apinaa_button = tk.Button(root, text="Kernesti hakee apinan ja antaa lapio", command=kernest_opastaa_apinaa)
canvas.create_window(900, 150, window=k_opasta_apinaa_button)

# Lisätään kaivamispainike
k_kaiva_button = tk.Button(root, text="Aloita Kernestin ojan kaivaminen", command=lambda: k_aloita_kaivaminen())
canvas.create_window(900, 200, window=k_kaiva_button)

# Ernestin Nappi fiksummalle kaivamiselle
k_fiksu_kaiva_button = tk.Button(root, text="Fiksu Kernestin ojan kaivaminen", command=lambda:k_aloita_fiksu_kaivaminen())
canvas.create_window(900, 250, window=k_fiksu_kaiva_button)

root.mainloop()

# Tulostetaan matriisit tarkistusta varten
print("Uima-altaan matriisi (tyhjä allas):")
print(allas_matriisi)

print("\nErnestin ojan matriisi (täynnä hiekkaa, arvo 1):")
print(ernestin_oja_matriisi)

print("\nKernestin ojan matriisi (täynnä hiekkaa, arvo 1):")
print(kernestin_oja_matriisi)
