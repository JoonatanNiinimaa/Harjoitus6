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
    viidakko_img = PhotoImage(file="viidakko.png").subsample(12, 12) 
    monkey_img = PhotoImage(file="monkey.png").subsample(6, 6) 
except Exception as e:
    print(f"Virhe kuvien lataamisessa: {e}")
    root.destroy()
    exit()

# Paikat ikkunassa
canvas = tk.Canvas(root, width=1200, height=800)
canvas.pack()
canvas.create_image(600, 400, image=saari_img)

# Uima-allas (muutettu väri kuvaamaan tyhjää allasta)
uima_allas_x1 = 575  
uima_allas_y1 = 375  
uima_allas_x2 = uima_allas_x1 + 60  
uima_allas_y2 = uima_allas_y1 + 20 
canvas.create_rectangle(uima_allas_x1, uima_allas_y1, uima_allas_x2, uima_allas_y2, fill="sandy brown", outline="brown") 

# Luodaan uima-allas matriisina (20x60, aluksi kaikki arvot ovat nollia)
allas_matriisi = np.zeros((20, 60))

# Ojat matriiseina 
ernestin_oja_matriisi = np.ones((100, 1))  # Ernestin oja
kernestin_oja_matriisi = np.ones((100, 1))  # Kernestin oja

# Ernestin oja 
ernest_ojan_x1 = uima_allas_x1 
ernest_ojan_y1 = uima_allas_y1  
ernest_ojan_x2 = ernest_ojan_x1  
ernest_ojan_y2 = ernest_ojan_y1 - 100  
canvas.create_line(ernest_ojan_x1, ernest_ojan_y1, ernest_ojan_x2, ernest_ojan_y2, fill="sandy brown", width=2)

# Kernestin oja
kernest_ojan_x1 = uima_allas_x2  
kernest_ojan_y1 = uima_allas_y1 
kernest_ojan_x2 = kernest_ojan_x1  
kernest_ojan_y2 = kernest_ojan_y1 - 100  
canvas.create_line(kernest_ojan_x1, kernest_ojan_y1, kernest_ojan_x2, kernest_ojan_y2, fill="sandy brown", width=2)

def tayta_ja_nollaa_oja():
    global apinat  
    
    for i in range(len(ernestin_oja_matriisi)):
        ernestin_oja_matriisi[i][0] = 1  
    for i in range(len(kernestin_oja_matriisi)):
        kernestin_oja_matriisi[i][0] = 1  

    # Poistetaan apinat ojalta ja nollataan niiden kaivamisindeksit
    for apina in apinat:
        # Poistetaan apinan kuva ensin
        if 'image' in apina and apina['image'] is not None and apina['ojalla'] == True:
            canvas.delete(apina['image']) 
            apina['image'] = None 
        
        # Asetetaan apina pois ojalta vasta kuvan poistamisen jälkeen
        apina['ojalla'] = False
        apina['kaivamis_index'] = 0
    paivita_oja_visuals()

    print("Ojien arvot on nollattu ja apinat poistettu ojalta.")

def paivita_oja_visuals():
    for i in range(len(ernestin_oja_matriisi)):
        kaivetun_osan_y = ernest_ojan_y1 - (i * (100 / len(ernestin_oja_matriisi)))
        current_color = hiekan_vari(1) 
        canvas.create_rectangle(ernest_ojan_x1, kaivetun_osan_y, ernest_ojan_x1 + 3, kaivetun_osan_y + (100 / len(ernestin_oja_matriisi)), fill=current_color, outline="")

    for i in range(len(kernestin_oja_matriisi)):
        kaivetun_osan_y = kernest_ojan_y1 - (i * (100 / len(kernestin_oja_matriisi)))
        current_color = hiekan_vari(1)
        canvas.create_rectangle(kernest_ojan_x1, kaivetun_osan_y, kernest_ojan_x1 + 3, kaivetun_osan_y + (100 / len(kernestin_oja_matriisi)), fill=current_color, outline="")

    print("Oja on päivitetty visuaalisesti.")

# Tilamuuttujat meriveden äänen toistamiseksi
ernestin_oja_ready = False
kernestin_oja_ready = False
first_ready_oja = None  # Tallennetaan ensimmäisenä valmistunut oja

def tarkista_uima_allas():
    global ernestin_oja_ready, kernestin_oja_ready, first_ready_oja
    while True:
        # Tarkista, onko molemmat ojat tyhjentyneet
        oja1_kaivettu = all(section[0] <= 0 for section in ernestin_oja_matriisi)
        oja2_kaivettu = all(section[0] <= 0 for section in kernestin_oja_matriisi)

        # Tarkistetaan ja muutetaan oja(t) siniseksi, jos kaikki sen osat ovat tyhjentyneet
        if oja1_kaivettu and not ernestin_oja_ready:
            print("Ernestin oja muuttuu siniseksi, koska kaikki osat ovat tyhjentyneet.")
            canvas.create_line(ernest_ojan_x1, ernest_ojan_y1, ernest_ojan_x2, ernest_ojan_y2, fill="blue")
            winsound.PlaySound("meri.wav", winsound.SND_FILENAME)
            ernestin_oja_ready = True  
            if first_ready_oja is None: 
                first_ready_oja = "Ernesti"

        if oja2_kaivettu and not kernestin_oja_ready:
            print("Kernestin oja muuttuu siniseksi, koska kaikki osat ovat tyhjentyneet.")
            canvas.create_line(kernest_ojan_x1, kernest_ojan_y1, kernest_ojan_x2, kernest_ojan_y2, fill="blue")
            winsound.PlaySound("meri.wav", winsound.SND_FILENAME)
            kernestin_oja_ready = True  
            if first_ready_oja is None:  
                first_ready_oja = "Kernesti"

        # Muuta uima-allasta siniseksi, jos molemmat ojat ovat tyhjät
        if oja1_kaivettu and oja2_kaivettu:
            print("Uima-allas muuttuu siniseksi, koska molemmat ojat ovat tyhjät.")
            canvas.create_rectangle(uima_allas_x1, uima_allas_y1, uima_allas_x2, uima_allas_y2, fill="blue")
            winsound.PlaySound("uimavesi.wav", winsound.SND_FILENAME)
            # Ilmaise äänimerkillä kumpi oja valmistui ensimmäisenä
            if first_ready_oja == "Ernesti":
                print("Ernestin oja oli ensimmäisenä valmis. Soitetaan matala ääni.")
                winsound.Beep(400, 10000)  # 400 Hz, 10 sekuntia
            elif first_ready_oja == "Kernesti":
                print("Kernestin oja oli ensimmäisenä valmis. Soitetaan kimeä ääni.")
                winsound.Beep(1000, 10000)  # 1000 Hz, 10 sekuntia
            break  
        time.sleep(1)  
# Luodaan ja käynnistetään säie uima-allaan tarkistamiseen
uima_allas_tarkistus_säie = threading.Thread(target=tarkista_uima_allas)
uima_allas_tarkistus_säie.start()

# Lisätään metsäalueet saarelle kolmeen kohtaan
metsan_paikat = [(425, 325), (775, 300), (750, 420)] 
for (x, y) in metsan_paikat:
    canvas.create_image(x, y, image=viidakko_img)

# Ernestin ja Kernestin paikat
ernesti_pos = (550, 440)
kernesti_pos = (650, 440)
ernesti = canvas.create_image(*ernesti_pos, image=ernesti_img)
kernesti = canvas.create_image(*kernesti_pos, image=kernesti_img)

# Apinat metsään
apinat = []
apina_lkm = 30  # Määrä apinoita, voi muuttaa

for i in range(apina_lkm):
    metsa_x, metsa_y = random.choice(metsan_paikat)  
    apinan_pos = (metsa_x + random.randint(-50, 50), metsa_y + random.randint(-30, 30))  # Satunnainen sijainti apinalle
    apina = canvas.create_image(*apinan_pos, image=monkey_img)
    apinat.append({'image': apina, 'has_shovel': False, 'ojalla': False, 'kaivamis_index': None})

# Liikuttaminen kohti kohdetta
def liiku_objekti(objekti, kohde_x, kohde_y):
    while True:  
        obj_x, obj_y = canvas.coords(objekti) 
        if abs(obj_x - kohde_x) < 1 and abs(obj_y - kohde_y) < 1:
            canvas.coords(objekti, kohde_x, kohde_y)  
            break  
        uusi_x = obj_x + (kohde_x - obj_x) / 10  
        uusi_y = obj_y + (kohde_y - obj_y) / 10  
        canvas.coords(objekti, uusi_x, uusi_y)
        time.sleep(0.02)

def ernest_opastaa_apinaa():
    if apinat:  
        # Etsi lähin apina, joka ei ole ojalla
        apina_distances = []
        ernest_x, ernest_y = canvas.coords(ernesti)  
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
        apina_x, apina_y = canvas.coords(apina_image)
        threading.Thread(target=liiku_objekti, args=(ernesti, apina_x, apina_y)).start()  
        # Kun Ernesti on saapunut apinalle, anna lapio
        root.after(1000, lambda: e_anna_lapio(closest_apina, apina_image))

def kernest_opastaa_apinaa():
    if apinat:  
        # Etsi lähin apina, joka ei ole ojalla
        apina_distances = []
        kernest_x, kernest_y = canvas.coords(kernesti)  
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
        apina_image = closest_apina['image']
        apina_x, apina_y = canvas.coords(apina_image)
        threading.Thread(target=liiku_objekti, args=(kernesti, apina_x, apina_y)).start()

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
                    winsound.Beep(500, 100)  # Kaivamisen ääni
                    oja_matriisi[oja_index][0] -= 1  # Vähennetään arvoa, jotta se merkitsee kaivettua
                    print(f"{apina['nimi']}n apina kaivoi ojan kohdasta: {oja_index}")

                    # Muuta hiekan väriä syvyyden mukaan
                    depth = oja_matriisi[oja_index][0]  # Käytetään matriisin arvoa syvyyden määrittämiseen
                    kaivetun_osan_y = oja_y1 - (oja_index * (100 / len(oja_matriisi)))
                else:
                    # Oja on jo kaivettu tai syvyys on negatiivinen
                    print(f"{apina['nimi']} ei voi kaivaa enää, oja on jo valmis kohdassa {oja_index}.")

                # Vähennä indeksiä
                apina['kaivamis_index'] += 1

                # Ajan laskeminen
                kaivamis_aika = 1 * (2 ** (apina['kaivamis_index'] - 1))
                if kaivamis_aika > 30:
                    kaivamis_aika = 30 # Tuli ongelmia jos aika kasvaisi loputtomiin 

                # Tarkista, onko kaivaminen valmis
                if apina['kaivamis_index'] >= len(oja_matriisi):
                    # Tarkista, onko koko oja kaivettu (kaikki 0 tai pienempiä)
                    if all(section[0] <= 0 for section in oja_matriisi):
                        # Muuta koko oja siniseksi, kun kaikki on kaivettu
                        for i in range(len(oja_matriisi)):
                            kaivetun_osan_y = oja_y1 - (i * (100 / len(oja_matriisi)))
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

    # Merkitse apina olevan ojalla ja tallenna indeksi
    apina['ojalla'] = True  
    apina['kaivamis_index'] = random.randint(0, len(ernestin_oja_matriisi) - 1)  # Aloita kaivaminen 

    # Siirrä apina ojan kohdalle
    uusi_x = ernest_ojan_x1 
    uusi_y = ernest_ojan_y1 - (apina['kaivamis_index'] * (100 / len(ernestin_oja_matriisi)))  # Apinan y-koordinaatti ojan alueella

    threading.Thread(target=liiku_objekti, args=(apina_image, uusi_x, uusi_y)).start()  # Siirrä apina ojalle

# Lisätään kaivamispainike
def k_anna_lapio(apina, apina_image):
    # Anna apinalle lapio
    apina['has_shovel'] = True
    print("Apina on saanut lapion:", apina)
    apina['nimi'] = 'Kernesti'  # Aseta apinan nimi

    apina['ojalla'] = True  
    apina['kaivamis_index'] = random.randint(0, len(kernestin_oja_matriisi) - 1)  

    uusi_x = kernest_ojan_x1  
    uusi_y = kernest_ojan_y1 - (apina['kaivamis_index'] * (100 / len(kernestin_oja_matriisi))) 

    threading.Thread(target=liiku_objekti, args=(apina_image, uusi_x, uusi_y)).start()

# Aloita kaivaminen
def e_aloita_kaivaminen():
    kaivettavat_apinat = []  # Lista kaivettavista apinoista
    for apina in apinat:
        if apina['has_shovel'] and apina['ojalla'] and apina['nimi'] == 'Ernesti':
            kaivettavat_apinat.append(apina)  # Lisää kaivettavat apinat listaan

    if kaivettavat_apinat:
        for apina in kaivettavat_apinat:
            apina['kaivamis_index'] = apina['kaivamis_index']  
            kaivaa(apina)  # Aloita kaivaminen jokaiselle apinalle
    else:
        print("Ei yhtään Ernestin apinaa, jolla on lapio.")

def k_aloita_kaivaminen():
    kaivettavat_apinat = []  
    for apina in apinat:
        if apina['has_shovel'] and apina['ojalla'] and apina['nimi'] == 'Kernesti':
            kaivettavat_apinat.append(apina)  

    if kaivettavat_apinat:
        for apina in kaivettavat_apinat:
            apina['kaivamis_index'] = apina['kaivamis_index']  
            kaivaa(apina)  
    else:
        print("Ei yhtään Ernestin apinaa, jolla on lapio.")

def e_aloita_fiksu_kaivaminen():
    # Fiksun kaivamislogiikka, jossa 10 apinaa kaivaa kohtia missä on hiekkaa (matriisin arvo = 1)
    kaivettavat_apinat = [apina for apina in apinat if not apina.get('has_shovel')]  # Suodata apinat, joilla ei ole lapioa

    # Ota vain 10 apinaa
    kaivettavat_apinat = kaivettavat_apinat[:10]  # Rajoita 10 apinaan

    # Anna kullekin apinalle lapio ja aloita kaivaminen sekunnin välein
    if kaivettavat_apinat:
        for i, apina in enumerate(kaivettavat_apinat):
            # Anna apinalle lapio
            e_anna_lapio(apina, apina['image'])
            root.after(i * 2000, lambda apina=apina: e_sijoita_ja_aloita_kaivaminen(apina))
    else:
        print("Ei yhtään apinaa, jolla ei ole lapioa.")

def e_sijoita_ja_aloita_kaivaminen(apina):
    # Sijoitetaan apinat 
    saatavilla_olevat = [indeksi for indeksi in range(len(ernestin_oja_matriisi)) if ernestin_oja_matriisi[indeksi][0] == 1]

    if saatavilla_olevat:
        # Valitse satunnainen indeksi saatavilla olevista
        indeksi = random.choice(saatavilla_olevat)

        # Sijoita apina ojan varrelle
        oja_x1 = ernest_ojan_x1
        oja_y1 = ernest_ojan_y1
        apina['kaivamis_index'] = indeksi  # Sijoitetaan apina ojan kohtaan "indeksi"
        
        uusi_x = oja_x1  
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
        piilota_apina(apina)  # Ei ole kaivettavaan niin piilotetaan apina

def k_aloita_fiksu_kaivaminen():
    # Sama kuin Ernestillä
    kaivettavat_apinat = [apina for apina in apinat if not apina.get('has_shovel')] 

    kaivettavat_apinat = kaivettavat_apinat[:10]  

    if kaivettavat_apinat:
        for i, apina in enumerate(kaivettavat_apinat):
            k_anna_lapio(apina, apina['image'])
            root.after(i * 1000, lambda apina=apina: k_sijoita_ja_aloita_kaivaminen(apina))
    else:
        print("Ei yhtään apinaa, jolla ei ole lapioa.")

def k_sijoita_ja_aloita_kaivaminen(apina):
    saatavilla_olevat = [indeksi for indeksi in range(len(kernestin_oja_matriisi)) if kernestin_oja_matriisi[indeksi][0] == 1]

    if saatavilla_olevat:
        indeksi = random.choice(saatavilla_olevat)

        oja_x1 = kernest_ojan_x1
        oja_y1 = kernest_ojan_y1
        apina['kaivamis_index'] = indeksi  
        uusi_x = oja_x1  
        uusi_y = oja_y1 - (indeksi * (100 / len(kernestin_oja_matriisi)))
        
        threading.Thread(target=liiku_objekti, args=(apina['image'], uusi_x, uusi_y)).start()
        kaivaa(apina)
        
        kernestin_oja_matriisi[indeksi][0] = 0
        root.after(1000, lambda: k_sijoita_ja_aloita_kaivaminen(apina))  # Jatketaan seuraavaan satunnaiseen paikkaan
    else:
        piilota_apina(apina)  

def piilota_apina(apina):
    # Lopulta piilottaa apinan ojalta
    if 'image' in apina and apina['image'] is not None:
        canvas.itemconfig(apina['image'], state='hidden')  
        apina['image'] = None  
        apina['ojalla'] = False 
        apina['kaivamis_index'] = 0 
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
    # Tarkista Ernestin ja Kernestin ojien arvot 
    print(ernestin_oja_matriisi)
    print(kernestin_oja_matriisi)

# Lisätään napit tarkistaakseen ojalla olevat apinat, tarkistamaan ojien arvot ja täyttämään ojat
tarkista_button = tk.Button(root, text="Tarkista ojalla olevat apinat", command=tarkista_ojalla_olevat_apinat)
canvas.create_window(600, 150, window=tarkista_button)

tarkista_ojamatriisi =tk.Button(root, text="Tarkista ojien arvot",command=tarkista_ojamatriisi)
canvas.create_window(600, 200, window=tarkista_ojamatriisi)

tayta_oja_button = tk.Button(root, text="Täytä ojat", command=tayta_ja_nollaa_oja)
canvas.create_window(600, 250, window=tayta_oja_button)

# Ernesti opastaa apinaa
e_opasta_apinaa_button = tk.Button(root, text="Ernesti hakee apinan ja antaa lapio", command=ernest_opastaa_apinaa)
canvas.create_window(350, 150, window=e_opasta_apinaa_button)

# Ernestin kaivamis nappi
e_kaiva_button = tk.Button(root, text="Aloita Ernestin ojan kaivaminen", command=lambda: e_aloita_kaivaminen())
canvas.create_window(350, 200, window=e_kaiva_button)

# Ernestin Nappi fiksummalle kaivamiselle
e_fiksu_kaiva_button = tk.Button(root, text="Fiksu Ernestin ojan kaivaminen", command=lambda:e_aloita_fiksu_kaivaminen())
canvas.create_window(350, 250, window=e_fiksu_kaiva_button)

# Kernesti opastaa apinaa
k_opasta_apinaa_button = tk.Button(root, text="Kernesti hakee apinan ja antaa lapio", command=kernest_opastaa_apinaa)
canvas.create_window(900, 150, window=k_opasta_apinaa_button)

# Kernestin kaivamis nappi
k_kaiva_button = tk.Button(root, text="Aloita Kernestin ojan kaivaminen", command=lambda: k_aloita_kaivaminen())
canvas.create_window(900, 200, window=k_kaiva_button)

# Ernestin Nappi fiksummalle kaivamiselle
k_fiksu_kaiva_button = tk.Button(root, text="Fiksu Kernestin ojan kaivaminen", command=lambda:k_aloita_fiksu_kaivaminen())
canvas.create_window(900, 250, window=k_fiksu_kaiva_button)

root.mainloop()
