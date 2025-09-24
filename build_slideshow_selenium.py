# Inhalte abrufen und Kopf/Fuß entfernen
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

                # Entferne Links mit href, die "Oberartikel" enthalten
                for tag in soup.find_all("a", href=True):
                    if "Oberartikel" in tag["href"] or "Zum Oberartikel" in tag.text:
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
