import tkinter as tk
from tkinter import PhotoImage
import numpy as np

root = tk.Tk()
root.title("Ernesti ja Kernestin uima-allas")
root.geometry("1200x800")

# Kuvien lataaminen ja koon muokkaaminen
try:
    saari_img = PhotoImage(file="saari.png")
    ernesti_img = PhotoImage(file="erne.png").subsample(4, 4)
    kernesti_img = PhotoImage(file="kerne.png").subsample(4, 4)
    viidakko_img = PhotoImage(file="viidakko.png").subsample(7, 7)  # Pienennetään viidakko.png kuvaa
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
metsan_paikat = [(200, 150), (1000, 300), (900, 500)]  # Sijainnit metsäalueille
for (x, y) in metsan_paikat:
    canvas.create_image(x, y, image=viidakko_img)

# Ernestin ja Kernestin paikat (säilytetään ennallaan)
ernesti_pos = (200, 400)
kernesti_pos = (600, 400)
ernesti = canvas.create_image(*ernesti_pos, image=ernesti_img)
kernesti = canvas.create_image(*kernesti_pos, image=kernesti_img)

root.mainloop()

# Tulostetaan matriisit tarkistusta varten
print("Uima-altaan matriisi (tyhjä allas):")
print(allas_matriisi)

print("\nErnestin ojan matriisi (täynnä hiekkaa, arvo 1):")
print(ernestin_oja_matriisi)

print("\nKernestin ojan matriisi (täynnä hiekkaa, arvo 1):")
print(kernestin_oja_matriisi)
