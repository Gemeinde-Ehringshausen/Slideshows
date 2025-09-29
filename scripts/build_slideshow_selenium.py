import json
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time

# Ordner für Konfigurationen und Ausgaben
CONFIG_FOLDER = "config"
OUTPUT_FOLDER = "slideshows"

# Headless Chrome konfigurieren
options = webdriver.ChromeOptions()
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--window-size=1920,1080")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Konfigurationsdatei für Dillwiese
config_file = "dillwiese_config.json"
config_path = os.path.join(CONFIG_FOLDER, config_file)

with open(config_path, "r", encoding="utf-8") as file:
    config = json.load(file)

links = config["urls"]
titles = config["titles"]
slide_duration = config["duration"] * 1000  # Dauer in Millisekunden

contents = []
for url in links:
    try:
        print(f"➡ Lade URL: {url}")
        driver.get(url)
        time.sleep(2)  # JS warten lassen
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        main_content = soup.find("div", class_="infoportal")
        if main_content:
            contents.append(str(main_content))
        else:
            print(f"⚠ Kein <div class='infoportal'> gefunden für {url}")
    except Exception as e:
        print(f"❌ Fehler bei {url}: {e}")

driver.quit()

# HTML für die Slideshow generieren
slideshow_name = "dillwiese_slideshow.html"
output_path = os.path.join(OUTPUT_FOLDER, slideshow_name)

html_template = f"""<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<title>Dillwiese Slideshow</title>
<style>
body, html {{
    margin: 0;
    padding: 0;
    width: 100%;
    height: 100%;
    background: #000;
    font-family: sans-serif;
}}
.slide {{
    display: none;
    width: 100%;
    height: 100%;
    box-sizing: border-box;
    padding: 1rem;
    background: #fff;
    overflow: auto;
    color: #000;
}}
.slide.active {{
    display: block;
}}
.progress-bar-container {{
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 5px;
    background: rgba(255, 255, 255, 0.3);
    z-index: 1000;
}}
.progress-bar {{
    width: 0;
    height: 100%;
    background: #00ff00;
    transition: width linear;
}}
.titles-container {{
    position: fixed;
    top: 10px;
    left: 50%;
    transform: translateX(-50%);
    text-align: center;
    z-index: 1001;
}}
.title {{
    display: inline-block;
    margin: 0 10px;
    font-size: 18px;
    color: gray;
    transition: color linear;
}}
.title.active {{
    color: green;
}}
</style>
</head>
<body>
<div class="progress-bar-container"><div class="progress-bar" id="progress-bar"></div></div>
<div class="titles-container">
"""

for i, title in enumerate(titles):
    html_template += f'<span class="title" id="title{i}">{title}</span>'


html_template += """
</div>
"""

for i, content in enumerate(contents):
    html_template += f'<div class="slide" id="slide{i}">{content}</div>'


html_template += f"""
<script>
let index = 0;
const slides = document.querySelectorAll('.slide');
const titles = document.querySelectorAll('.title');
const progressBar = document.getElementById('progress-bar');
const slideDuration = {slide_duration};
function resetProgressBar() {{
    progressBar.style.transition = 'none';
    progressBar.style.width = '0%';
    setTimeout(() => {{
        progressBar.style.transition = `width ${slide_duration}ms linear`;
        progressBar.style.width = '100%';
    }}, 50);
}}
function resetTitles() {{
    titles.forEach(title => title.classList.remove('active'));
    titles[index].classList.add('active');
}}
function showSlide(i) {{
    slides.forEach(slide => slide.classList.remove('active'));
    slides[i].classList.add('active');
}}
function showNext() {{
    index = (index + 1) % slides.length;
    showSlide(index);
    resetProgressBar();
    resetTitles();
}}
if (slides.length > 0) {{
    showSlide(0);
    resetProgressBar();
    resetTitles();
    setInterval(showNext, slideDuration);
}}
</script>
</body>
</html>
"""

with open(output_path, "w", encoding="utf-8") as f:
    f.write(html_template)

print(f"🎉 Slideshow für Dillwiese erstellt: {output_path}")

