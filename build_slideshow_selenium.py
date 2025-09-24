from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time

BASE_URL = "https://www.webkita.de/ehringshausen/infoportal/"

# Liste der Unterseiten (manuell oder automatisch vom Startlink abrufen)
links = [
    "https://www.webkita.de/ehringshausen/infoportal/",
    "https://www.webkita.de/ehringshausen/infoportal/anleitung?7",
    # hier weitere Links ergänzen
]

# Headless Chrome konfigurieren
options = webdriver.ChromeOptions()
options.add_argument("--headless=new")   # neuer Headless-Modus
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--window-size=1920,1080")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

contents = []

for url in links:
    try:
        driver.get(url)
        time.sleep(2)  # kurz warten, bis JS lädt

        # Mittelteil extrahieren
        try:
            element = driver.find_element(By.CSS_SELECTOR, "main")  # Hauptbereich
            html = element.get_attribute("outerHTML")
            contents.append(html)
        except:
            print("⚠ Kein main gefunden, ganze Seite verwenden:", url)
            contents.append(driver.page_source)
    except Exception as e:
        print("❌ Fehler bei:", url, e)

driver.quit()

# Slideshow HTML bauen
html_template = """<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<title>Infoportal Slideshow</title>
<style>
body, html {
  margin:0; padding:0;
  width:100vw; height:100vh;
  background:black;
  overflow:hidden;
  font-family:sans-serif;
}
.slide { display:none; width:100vw; height:100vh; overflow:hidden; box-sizing:border-box; padding:2rem; color:#fff; background:#222;}
.slide.active { display:block; }
img, iframe { max-width:100%; max-height:100%; }
</style>
</head>
<body>
"""

for i, content in enumerate(contents):
    html_template += f'<div class="slide" id="slide{i}">{content}</div>\n'

html_template += """
<script>
let index=0;
const slides=document.querySelectorAll('.slide');
function showNext() {
 slides.forEach(s=>s.classList.remove('active'));
 slides[index].classList.add('active');
 index=(index+1)%slides.length;
}
showNext();
setInterval(showNext,10000);
</script>
</body>
</html>
"""

with open("slideshow.selenium.html","w",encoding="utf-8") as f:
    f.write(html_template)

print("✅ slideshow.html erstellt mit", len(contents), "Unterseiten")
