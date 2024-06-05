import os
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from selenium.common.exceptions import WebDriverException
import threading
import sys
import time
from selenium import webdriver


class AnalisiTypo:
    def __init__(self, master):
        self.prototypeDriver = None
        self.master = master
        self.master.title("Analisi typo")

        # Frame per le immagini e i testi degli URL
        self.image_text_frame = tk.Frame(self.master)
        self.image_text_frame.pack(pady=10)

        # Frame per i bottoni
        self.button_frame = tk.Frame(self.master)
        self.button_frame.pack(pady=10)

        self.button1 = tk.Button(self.button_frame, text="NotTypo", command=lambda: self.aggiorna_lista("NotTypo"))
        self.button1.pack(side="left", padx=5)

        self.button2 = tk.Button(self.button_frame, text="Typo", command=lambda: self.aggiorna_lista("Typo"))
        self.button2.pack(side="left", padx=5)

        self.button3 = tk.Button(self.button_frame, text="Down", command=lambda: self.aggiorna_lista("Down"))
        self.button3.pack(side="left", padx=5)

        self.button_avanti = tk.Button(self.button_frame, text="Avanti", command=self.prossima_coppia)
        self.button_avanti.pack(side="left", padx=5)

        self.loading_frame = None

        self.photo1 = None
        self.photo2 = None

        # URL originale corrente: per evitare di ricaricare sempre lo stesso immagine a sinistra
        self.current_original_url = None
        self.current_original_image= None

        # Inizializzo le etichette delle immagini
        self.label1 = tk.Label(self.image_text_frame)
        self.label1.grid(row=0, column=0, padx=10)

        self.label2 = tk.Label(self.image_text_frame)
        self.label2.grid(row=0, column=1, padx=10)

        # Lista di coppie di URL
        self.coppie_urls = []
        with open("test_domains.txt", "r") as file:
            for line in file:
                self.coppie_urls.append(line.strip().split(" - "))

        # Leggo il file
        with open("test_domains.txt", "r") as file:
            self.lines = file.readlines()

        # prendo l'indice da cui partire
        try:
            with open("indice.txt", "r") as file:
                self.indice_corrente = int(file.read())
        except FileNotFoundError:
            self.indice_corrente = 0

        if self.indice_corrente >= len (self.coppie_urls):
            messagebox.showinfo("Fine del file", "Hai analizzato tutte le coppie di URL.")
            return

        #Semaforo
        self.mutex=threading.Semaphore(5)

        thread=threading.Thread(target=self.cattura_schermate, args=())
        thread.daemon=True
        thread.start()

        time.sleep(20)

        self.mostra_immagini()

    def inizializzazione(self):
        options = webdriver.ChromeOptions()
        #options.add_argument("--headless")  #**NON FUNZIONA**
        options.add_argument("--window-position=-2000,0")
        options.add_argument("--start-minimized")
        options.add_argument("--disable-web-security")
        options.add_argument("--allow-running-insecure-content")
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--ignore-ssl-errors")
        chrome_path = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
        options.binary_location = chrome_path
        options.add_extension("I-don-t-care-about-cookies.crx")

        driver = webdriver.Chrome(options=options)
        try:
            driver.get("https://chromewebstore.google.com/detail/i-dont-care-about-cookies/fihnjjcciajhdojfnbdddfaoknhalnja")
            time.sleep(5)
        finally:
            return driver


    def fai_screenshot(self, url):
        self.mutex.acquire()
        driver= self.inizializzazione()
        try:
            driver.get("https://" + url)
            time.sleep(5)
            driver.save_screenshot(f"fotositi/{url}.png")
            print(url + " salvato con https")
        except WebDriverException:
            print(f"Errore durante il caricamento di {url} con https")
            try:
                driver.get("http://" + url)
                time.sleep(5)
                driver.save_screenshot(f"fotositi/{url}.png")
                print(url + " salvato con http")
            except WebDriverException:
                print(f"Errore durante il caricamento di {url} con http: il sito è down")
                image1 = Image.new("RGB", (500, 500), "yellow")
                image1.save(f"fotositi/{url}.png")
                print(url + " segnaposto salvato")
        finally:
            driver.quit()
            self.mutex.release()


    def cattura_schermate(self):
        for idx, url_pair in enumerate(self.coppie_urls[self.indice_corrente: ], start=self.indice_corrente):
            print("Download " + url_pair[0] + " " + url_pair[1])
            urlOriginale = url_pair[0]
            urlTypo = url_pair[1]
            if urlOriginale != self.current_original_url:
                self.current_original_url = urlOriginale
                thread1 = threading.Thread(target=self.fai_screenshot, args=(urlOriginale,))
                thread1.daemon=True
                thread1.start()
            thread2 = threading.Thread(target=self.fai_screenshot, args=(urlTypo,))
            thread2.daemon=True
            thread2.start()
            time.sleep(3)


    def mostra_immagini(self):
        url_originale, url_typo = self.coppie_urls[self.indice_corrente]
        original_ready = os.path.exists(f"fotositi/{url_originale}.png")
        typo_ready = os.path.exists(f"fotositi/{url_typo}.png")
        if original_ready and typo_ready:
            self.aggiornaImageOriginale(url_originale)
            self.aggiornaImageTypo(url_typo)
            self.riattiva_pulsanti()
        else:
            self.mostra_immagini_loading()
            self.master.after(1000, self.mostra_immagini)


    def disabilita_pulsanti(self):
        for button in [self.button1, self.button2, self.button3, self.button_avanti]:
            button.config(state="disabled")


    def riattiva_pulsanti(self):
        for button in [self.button1, self.button2, self.button3, self.button_avanti]:
            button.config(state="normal")


    def mostra_immagini_loading(self):
        self.disabilita_pulsanti()
        loading_image = Image.open("loading.png").resize((500, 500))
        for widget in self.image_text_frame.winfo_children():
            widget.destroy()
        self.photo1 = ImageTk.PhotoImage(loading_image)
        self.photo2 = ImageTk.PhotoImage(loading_image)
        self.label1 = tk.Label(self.image_text_frame, image=self.photo1)
        self.label1.grid(row=0, column=0, padx=10)
        url_originale_label = tk.Label(self.image_text_frame, text="ATTENDERE CARICAMENTO")
        url_originale_label.grid(row=1, column=0, padx=10)
        self.label2 = tk.Label(self.image_text_frame, image=self.photo2)
        self.label2.grid(row=0, column=1, padx=10)
        url_typo_label = tk.Label(self.image_text_frame, text="ATTENDERE CARICAMENTO")
        url_typo_label.grid(row=1, column=1, padx=10)

    def aggiornaImageOriginale(self, url_originale):
        image1 = Image.open(f"fotositi/{url_originale}.png").resize((500, 500))
        self.photo1 = ImageTk.PhotoImage(image1)
        self.label1.configure(image=self.photo1)
        url_originale_label = tk.Label(self.image_text_frame, text=f"URL ORIGINALE: {url_originale}")
        url_originale_label.grid(row=1, column=0, padx=10)
        self.current_original_url = url_originale


    def aggiornaImageTypo(self, url_typo):
        image2 = Image.open(f"fotositi/{url_typo}.png").resize((500, 500))
        self.photo2 = ImageTk.PhotoImage(image2)
        self.label2.configure(image=self.photo2)
        url_typo_label = tk.Label(self.image_text_frame, text=f"URL TYPO:     {url_typo}")
        url_typo_label.grid(row=1, column=1, padx=10)


    def prossima_coppia(self):
        self.indice_corrente += 1
        if self.indice_corrente == len(self.coppie_urls):
            messagebox.showinfo("Fine del file", "Hai analizzato tutte le coppie di URL.")
            self.chiudi_finestra()
            return
        self.mostra_immagini()



    def aggiorna_lista(self, button_text):
        url_originale, url_typo = self.coppie_urls[self.indice_corrente]
        nuova_coppia = f"{url_originale} - {url_typo} - {button_text}\n"
        for i, line in enumerate(self.lines):
            if line.strip() == f"{url_originale} - {url_typo}":
                self.lines[i] = nuova_coppia
                break
        self.prossima_coppia()


    def salva_indice(self):
        with open("indice.txt", "w") as file:
            file.write(str(self.indice_corrente + 1))


    def chiudi_finestra(self):
        self.elimina_foto()
        self.salva_indice()
        with open("test_domains.txt", "w") as file:
            file.writelines(self.lines)
        self.master.destroy()
        sys.exit()


    def elimina_foto(self):
        foto_dir = "fotositi"
        if os.path.exists(foto_dir):
            for filename in os.listdir(foto_dir):
                file_path = os.path.join(foto_dir, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                except Exception as e:
                    print(f"Errore durante l'eliminazione del file {file_path}: {e}")


def main():
    if not os.path.exists("fotositi"):
        os.makedirs("fotositi")
    root = tk.Tk()
    app = AnalisiTypo(root)
    root.protocol("WM_DELETE_WINDOW", app.chiudi_finestra)
    root.mainloop()



if __name__ == "__main__":
    main()






