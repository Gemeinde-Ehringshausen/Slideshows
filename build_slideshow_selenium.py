from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import os

BASE_URL = "https://www.webkita.de/ehringshausen/infoportal/"

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
# Alle Unterseiten automatisch sammeln
# -----------------------------
print("🔎 Lade Startseite:", BASE_URL)
driver.get(BASE_URL)
time.sleep(2)  # JS warten lassen

# alle <a>-Links aus gerendertem DOM
elems = driver.find_elements(By.TAG_NAME, "a")
links = []
for e in elems:
    href = e.get_attribute("href")
    if href and "/infoportal/" in href:
        if href not in links:
            links.append(href)

print(f"📌 Gefundene Unterseiten: {len(links)}")
for l in links:
    print(" -", l)

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
                for selector in ["nav.navbar", "div.footer", "div.modal", "div.wk_notification_container"]:
                    for tag in soup.select(selector):
                        tag.decompose()
                
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
body, html {
margin:0; padding:0;
width:100%; height:100%;
background:#000;
font-family:sans-serif;
}
.slide {
display:none;
width:100%;
height:100%;
box-sizing:border-box;
padding:1rem;
background:#fff;
overflow:auto;
color:#000;
}
.slide.active { display:block; }
</style>
</head>
<body>
"""

for i, content in enumerate(contents):
    html_template += f'<div class="slide" id="slide{i}">{content}</div>'


html_template += """
<script>
let index = 0;
const slides = document.querySelectorAll('.slide');
function showSlide(i) {
    slides.forEach(s => s.classList.remove('active'));
    slides[i].classList.add('active');
}
function showNext() {
    index = (index + 1) % slides.length;
    showSlide(index);
}
if (slides.length > 0) {
    showSlide(0);
    setInterval(showNext, 10000);
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
