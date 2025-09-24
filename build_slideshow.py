import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.webkita.de/ehringshausen/infoportal/"

# 1. Startseite abrufen
res = requests.get(BASE_URL)
soup = BeautifulSoup(res.text, "html.parser")

# 2. Alle Links sammeln, die zum Infoportal gehören
links = []
for a in soup.find_all("a", href=True):
    href = a["href"]
    if href.startswith(BASE_URL):
        links.append(href)

# doppelte entfernen
links = list(dict.fromkeys(links))

# 3. Inhalte der Unterseiten extrahieren (nur Mittelteil)
contents = []
for url in links:
    try:
        page = requests.get(url)
        psoup = BeautifulSoup(page.text, "html.parser")

        # 🟢 Versuche den Hauptbereich zu finden
        main = (
            psoup.select_one("main") or
            psoup.select_one("article") or
            psoup.select_one("div.content") or
            psoup.select_one("div#content")
        )

        # Wenn nix gefunden → ganze Seite als Fallback
        if main:
            contents.append(str(main))
        else:
            print("⚠️ Kein Hauptbereich gefunden für:", url)
            contents.append(psoup.get_text())
    except Exception as e:
        print("❌ Fehler bei", url, ":", e)

# 4. Slideshow-HTML schreiben
html_template = """<!DOCTYPE html>
<html lang="de">
<head>
  <meta charset="UTF-8">
  <title>Infoportal Slideshow</title>
  <style>
    body, html {
      margin: 0;
      padding: 0;
      width: 100vw;
      height: 100vh;
      background: black;
      overflow: hidden;
      font-family: sans-serif;
    }
    .slide {
      display: none;
      width: 100vw;
      height: 100vh;
      overflow: hidden;
      box-sizing: border-box;
      padding: 2rem;
      color: #fff;
      background: #222;
    }
    .slide.active {
      display: block;
    }
    img, iframe {
      max-width: 100%;
      max-height: 100%;
    }
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

function showNext() {
  slides.forEach(s => s.classList.remove('active'));
  slides[index].classList.add('active');
  index = (index + 1) % slides.length;
}

showNext();
setInterval(showNext, 10000); // 10 Sekunden
</script>
</body>
</html>
"""

with open("slideshow.html", "w", encoding="utf-8") as f:
    f.write(html_template)

print("✅ slideshow.html erstellt mit", len(contents), "Unterseiten (nur Mittelteil).")
