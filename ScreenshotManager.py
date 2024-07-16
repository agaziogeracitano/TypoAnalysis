from PIL import Image
from selenium.common.exceptions import WebDriverException
import threading
import time
from selenium import webdriver


class ScreenshotManager:
    def __init__(self):
        self.mutex = threading.Semaphore(5)
        self.current_original_url = None

    def inizializzazione(self):
        options = webdriver.ChromeOptions()
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
        driver = self.inizializzazione()
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

    def cattura_schermate(self, coppie_urls, indice_corrente):
        for idx, url_pair in enumerate(coppie_urls[indice_corrente:], start=indice_corrente):
            print("Download " + url_pair[0] + " " + url_pair[1])
            urlOriginale = url_pair[0]
            urlTypo = url_pair[1]
            if urlOriginale != self.current_original_url:
                self.current_original_url = urlOriginale
                thread1 = threading.Thread(target=self.fai_screenshot, args=(urlOriginale,))
                thread1.daemon = True
                thread1.start()
            thread2 = threading.Thread(target=self.fai_screenshot, args=(urlTypo,))
            thread2.daemon = True
            thread2.start()
            time.sleep(3)
