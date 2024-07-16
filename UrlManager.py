class URLManager:
    def __init__(self, url_file, index_file):
        self.url_file = url_file
        self.indice_file = index_file
        self.coppie_urls = self.leggi_urls()
        self.lines = self.leggi_file()
        self.indice_corrente = self.leggi_indice()

    def leggi_urls(self):
        coppie = []
        with open(self.url_file, "r") as file:
            for line in file:
                coppie.append(line.strip().split(" - "))
        return coppie

    def leggi_file(self):
        with open(self.url_file, "r") as file:
            return file.readlines()

    def leggi_indice(self):
        try:
            with open(self.indice_file, "r") as file:
                return int(file.read())
        except FileNotFoundError:
            return 0

    def salva_indice(self, indice):
        with open(self.indice_file, "w") as file:
            file.write(str(indice))

    def aggiorna_lista(self, indice_corrente, button_text):
        url_originale, url_typo = self.coppie_urls[indice_corrente]
        nuova_coppia = f"{url_originale} - {url_typo} - {button_text}\n"
        for i, line in enumerate(self.lines):
            if line.strip() == f"{url_originale} - {url_typo}":
                self.lines[i] = nuova_coppia
                break
        self.salva_file()

    def salva_file(self):
        with open(self.url_file, "w") as file:
            file.writelines(self.lines)