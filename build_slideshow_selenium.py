from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import os

# -----------------------------
# Manuell einzutragende URLs und Überschriften
# -----------------------------
links = [
    "https://www.webkita.de/ehringshausen/infoportal/anleitung",
    "https://www.webkita.de/ehringshausen/infoportal/Info_Einrichtungen",
    "https://www.webkita.de/ehringshausen/infoportal/Formulare",
    "https://www.webkita.de/ehringshausen/infoportal/Satzungen_Gebuehren",
    "https://www.webkita.de/ehringshausen/infoportal/Leitbild"
]
titles = [
    "Anleitung",
    "Unsere Einrichtungen",
    "Formulare",
    "Gebühren und Satzungen",
    "Unser Leitbild"
]

# -----------------------------
# Headless Chrome konfigurieren
# -----------------------------
options = webdriver.ChromeOptions()
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--window-size=1920,1080")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# -----------------------------
# Inhalte abrufen und Kopf/Fuß entfernen
# -----------------------------
contents = []
for url in links:
    try:
        print(f"➡ Lade URL: {url}")
        driver.get(url)
        time.sleep(2)  # JS warten lassen
        try:
            # Gesamte Seite abrufen
            html = driver.page_source
            
            # BeautifulSoup verwenden, um den Inhalt zu parsen
            soup = BeautifulSoup(html, "html.parser")
            
            # Hauptinhalt extrahieren
            main_content = soup.find("div", class_="infoportal")
            if main_content:
                # Entferne Header, Footer und unnötige Elemente
                for selector in [
                    "nav.navbar",  # Header-Navigation
                    "div.footer",  # Footer
                    "div.modal",   # Modale Dialoge
                    "div.wk_notification_container",  # Benachrichtigungen
                    "div.pull-right",  # Suchfeld und Links (FAQ, Artikelübersicht)
                    "a[href*='infoportal-faq']",  # Link zu FAQ
                    "a[href*='infoportal-uebersicht']",  # Link zur Artikelübersicht
                ]:
                    for tag in soup.select(selector):
                        tag.decompose()

                # Entferne Links mit "Zum Oberartikel" im Text oder href
                for tag in main_content.find_all("a", href=True):
                    if "Oberartikel" in tag["href"] or "Zum Oberartikel" in tag.text.strip():
                        tag.decompose()

                # Entferne verdächtige `<div>`-Container, die den Link enthalten könnten
                for container in main_content.find_all("div"):
                    if "Oberartikel" in container.get_text(strip=True):
                        container.decompose()

                # Bereinigtes HTML speichern
                html = str(main_content)
                contents.append(html)
                print(f"✅ Inhalt aus <div class='infoportal'> geladen ({len(html)} Zeichen)")
            else:
                print("⚠ Kein <div class='infoportal'> gefunden, gesamte Seite genommen.")
                contents.append(driver.page_source)
        except Exception as e:
            print(f"⚠ Fehler beim Extrahieren des Inhalts: {e}")
            contents.append(driver.page_source)
    except Exception as e:
        print(f"❌ Fehler beim Laden von {url}: {e}")

driver.quit()

# -----------------------------
# Slideshow HTML bauen
# -----------------------------
html_template = """<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<title>Infoportal Slideshow</title>
<style>
/* Grundlayout */
body, html {
    margin: 0;
    padding: 0;
    width: 100%;
    height: 100%;
    background: #000;
    font-family: sans-serif;
}

/* Slideshow-Styling */
.slide {
    display: none;
    width: 100%;
    height: 100%;
    box-sizing: border-box;
    padding: 1rem;
    background: #fff;
    overflow: auto;
    color: #000;
}

.slide.active {
    display: block;
}

/* Fortschrittsbalken */
.progress-bar-container {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 5px;
    background: rgba(255, 255, 255, 0.3); /* Hintergrund des Containers */
    z-index: 1000; /* Immer sichtbar */
}

.progress-bar {
    width: 0;
    height: 100%;
    background: #00ff00; /* Farbe des Fortschrittsbalkens */
    transition: width linear;
}

/* Überschriften */
.titles-container {
    position: fixed;
    top: 10px;
    left: 50%;
    transform: translateX(-50%);
    text-align: center;
    z-index: 1001; /* Über der Slideshow */
}

.title {
    display: inline-block;
    margin: 0 10px;
    font-size: 18px;
    color: gray;
    transition: color linear;
}

.title.active {
    color: green;
}
</style>
</head>
<body>

<!-- Fortschrittsbalken -->
<div class="progress-bar-container">
    <div class="progress-bar" id="progress-bar"></div>
</div>

<!-- Überschriften -->
<div class="titles-container">
"""
# Überschriften hinzufügen
for i, title in enumerate(titles):
    html_template += f'<span class="title" id="title{i}">{title}</span>
'

html_template += """
</div>

<!-- Slideshow-Inhalte -->
"""

# Inhalte der Slides hinzufügen
for i, content in enumerate(contents):
    html_template += f'<div class="slide" id="slide{i}">{content}</div>
'

# JavaScript für die Slideshow und die Überschriften
html_template += """
<script>
/* JavaScript für die Slideshow, Fortschrittsbalken und Überschriften */

// Variablen für die Slideshow
let index = 0;
const slides = document.querySelectorAll('.slide');
const titles = document.querySelectorAll('.title');
const progressBar = document.getElementById('progress-bar');
const slideDuration = 10000; // Dauer pro Slide in Millisekunden (10 Sekunden)

// Funktion, um den Fortschrittsbalken zu animieren
function resetProgressBar() {
    progressBar.style.transition = 'none'; // Keine Animation für den Reset
    progressBar.style.width = '0%'; // Zurücksetzen
    setTimeout(() => {
        progressBar.style.transition = `width ${slideDuration}ms linear`; // Animation aktivieren
        progressBar.style.width = '100%'; // Fortschrittsbalken füllen
    }, 50); // Kleine Verzögerung, um den Reset sichtbar zu machen
}

// Funktion, um die Überschriften zu animieren
function resetTitles() {
    titles.forEach(title => title.classList.remove('active'));
    titles[index].classList.add('active');
}

// Funktion, um eine Slide anzuzeigen
function showSlide(i) {
    slides.forEach(slide => slide.classList.remove('active'));
    slides[i].classList.add('active');
}

// Funktion, um zur nächsten Slide zu wechseln
function showNext() {
    index = (index + 1) % slides.length; // Nächste Slide oder zurück zur ersten
    showSlide(index);
    resetProgressBar(); // Fortschrittsbalken zurücksetzen und starten
    resetTitles(); // Überschrift aktualisieren
}

// Slideshow starten
if (slides.length > 0) {
    showSlide(0); // Erste Slide anzeigen
    resetProgressBar(); // Fortschrittsbalken starten
    resetTitles(); // Erste Überschrift aktivieren
    setInterval(showNext, slideDuration); // Automatischer Wechsel nach der festgelegten Dauer
}
</script>
</body>
</html>
"""

# -----------------------------
# Datei schreiben
# -----------------------------
filename = "slideshow_selenium.html"

with open(filename, "w", encoding="utf-8") as f:
    f.write(html_template)

print(f"🎉 {filename} erstellt mit {len(contents)} Unterseiten")
print("Pfad:", os.path.abspath(filename))
