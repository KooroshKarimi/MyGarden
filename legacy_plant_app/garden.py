import json
import os

DATA_FILE = 'plants.json'

def load_plants():
    """Lädt die Pflanzenliste aus der JSON-Datei."""
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        # Fallback bei korrupter Datei
        return []
    except Exception as e:
        print(f"Fehler beim Laden der Pflanzen: {e}")
        return []

def save_plants(plants):
    """Speichert die Pflanzenliste in die JSON-Datei."""
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(plants, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Fehler beim Speichern der Pflanzen: {e}")

def get_garden_data():
    """
    Gibt eine Liste von Pflanzen-Dictionaries zurück.
    """
    return load_plants()

def update_plant_image(plant_id, filename):
    """
    Aktualisiert den Bildpfad einer Pflanze.
    """
    plants = load_plants()
    updated = False
    for plant in plants:
        if plant.get('id') == plant_id:
            plant['image'] = filename
            updated = True
            break
    
    if updated:
        save_plants(plants)
    return updated
