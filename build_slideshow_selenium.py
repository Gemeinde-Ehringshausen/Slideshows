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
# Alle Links aus dem Infoportal sammeln
# -----------------------------
driver.get(BASE_URL)
time.sleep(2)

soup = BeautifulSoup(driver.page_source, "html.parser")

links = []
for a in soup.find_all("a", href=True):
    href = a["href"]
    # nur interne Links zum Infoportal mitnehmen
    if href.startswith(BASE_URL) or href.startswith("anleitung") or href.startswith("?"):
        if not href.startswith("http"):  # relative Links ergänzen
            href = BASE_URL + href.lstrip("/")
        if href not in links:
            links.append(href)

print("📌 Gefundene Unterseiten:", len(links))
for l in links:
    print(" -", l)

# -----------------------------
# Inhalte abrufen
# -----------------------------
contents = []

for url in links:
    try:
        driver.get(url)
        time.sleep(2)  # warten bis JS geladen hat

        try:
            element = driver.find_element(By.CSS_SELECTOR, "main")  # nur Hauptbereich
            html = element.get_attribute("outerHTML")
            contents.append(html)
            print(f"✅ Inhalt aus <main> geladen: {url}")
        except:
            print(f"⚠ Kein <main> gefunden, gesamte Seite genommen: {url}")
            contents.append(driver.page_source)
    except Exception as e:
        print("❌ Fehler bei:", url, e)

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
    html_template += f'<div class="slide" id="slide{i}">{content}</div>\n'

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
  showSlide(0); // Erste Seite anzeigen
  setInterval(showNext, 10000); // alle 10 Sek wechseln
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
