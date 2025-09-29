from flask import Flask, request, jsonify, send_from_directory
import json
import os
import subprocess

# Flask-Server initialisieren
app = Flask(__name__)

# Ordnerpfade
CONFIG_FOLDER = "config"
OUTPUT_FOLDER = "slideshows"
SCRIPTS_FOLDER = "scripts"

# Route: Konfiguration speichern
@app.route('/save-config/<kita_name>', methods=['POST'])
def save_config(kita_name):
    config_data = request.get_json()
    config_path = os.path.join(CONFIG_FOLDER, f"{kita_name}_config.json")

    # Konfigurationsdatei speichern
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config_data, f, ensure_ascii=False, indent=4)

    return jsonify({"message": f"Konfiguration für {kita_name} gespeichert."})


# Route: Slideshow generieren
@app.route('/generate-slideshow/<kita_name>', methods=['POST'])
def generate_slideshow(kita_name):
    try:
        # Python-Skript ausführen
        subprocess.run(
            ["python", os.path.join(SCRIPTS_FOLDER, "build_slideshow_selenium.py")],
            check=True
        )
        return jsonify({"message": f"Slideshow für {kita_name} erfolgreich generiert."})
    except subprocess.CalledProcessError as e:
        return jsonify({"error": f"Fehler beim Generieren der Slideshow für {kita_name}: {str(e)}"}), 500


# Route: Zugriff auf generierte Slideshows
@app.route('/slideshows/<filename>', methods=['GET'])
def get_slideshow(filename):
    return send_from_directory(OUTPUT_FOLDER, filename)


# Route: Zugriff auf die Konfigurationsdateien
@app.route('/config/<filename>', methods=['GET'])
def get_config(filename):
    return send_from_directory(CONFIG_FOLDER, filename)


if __name__ == "__main__":
    # Server starten
    app.run(debug=True)

