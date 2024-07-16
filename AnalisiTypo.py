import os
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import threading
import sys
import time
from ScreenshotManager import ScreenshotManager
from UrlManager import URLManager


class AnalisiTypo:
    def __init__(self, master, url_manager, screenshot_manager):
        self.master = master
        self.master.title("Analisi typo")
        self.url_manager = url_manager
        self.screenshot_manager = screenshot_manager

        self.loading_frame = None
        self.photo1 = None
        self.photo2 = None

        self.image_text_frame = tk.Frame(self.master)
        self.image_text_frame.pack(pady=10)
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

        self.label1 = tk.Label(self.image_text_frame)
        self.label1.grid(row=0, column=0, padx=10)
        self.label2 = tk.Label(self.image_text_frame)
        self.label2.grid(row=0, column=1, padx=10)

        self.current_original_url = None

        if self.url_manager.indice_corrente >= len(self.url_manager.coppie_urls):
            messagebox.showinfo("Fine del file", "Hai analizzato tutte le coppie di URL.")
            return

        thread = threading.Thread(target=self.screenshot_manager.cattura_schermate, args=(self.url_manager.coppie_urls, self.url_manager.indice_corrente))
        thread.daemon = True
        thread.start()

        time.sleep(20)
        self.mostra_immagini()

    def mostra_immagini(self):
        url_originale, url_typo = self.url_manager.coppie_urls[self.url_manager.indice_corrente]
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
        self.url_manager.indice_corrente += 1
        if self.url_manager.indice_corrente == len(self.url_manager.coppie_urls):
            messagebox.showinfo("Fine del file", "Hai analizzato tutte le coppie di URL.")
            self.chiudi_finestra()
            return
        self.mostra_immagini()

    def aggiorna_lista(self, button_text):
        self.url_manager.aggiorna_lista(self.url_manager.indice_corrente, button_text)
        self.prossima_coppia()

    def chiudi_finestra(self):
        self.elimina_foto()
        self.url_manager.salva_indice(self.url_manager.indice_corrente + 1)
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
    url_manager = URLManager("test_domains.txt", "indice.txt")
    screenshot_manager = ScreenshotManager()
    app = AnalisiTypo(root, url_manager, screenshot_manager)
    root.protocol("WM_DELETE_WINDOW", app.chiudi_finestra)
    root.mainloop()

if __name__ == "__main__":
    main()
