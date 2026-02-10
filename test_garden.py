import pytest
import json
import os
import garden

# Dummy-Daten für die Tests
TEST_PLANTS = [
    {
        "id": 1,
        "name": "Monstera",
        "scientific_name": "Monstera deliciosa",
        "image": "/static/images/monstera.jpg",
        "water_needs": "Mittel",
        "status": "Gesund"
    },
    {
        "id": 2,
        "name": "Ficus",
        "scientific_name": "Ficus elastica",
        "image": "/static/images/ficus.jpg",
        "water_needs": "Wenig",
        "status": "Braucht Wasser"
    }
]

@pytest.fixture
def mock_garden_data(tmp_path, monkeypatch):
    """
    Erstellt eine temporäre plants.json und patcht garden.DATA_FILE,
    damit die Tests nicht die echte Datei überschreiben.
    """
    # Temporäre Datei erstellen
    d = tmp_path / "data"
    d.mkdir()
    p = d / "test_plants.json"
    
    # Testdaten schreiben
    with open(p, 'w', encoding='utf-8') as f:
        json.dump(TEST_PLANTS, f)
    
    # garden.DATA_FILE patchen
    monkeypatch.setattr(garden, 'DATA_FILE', str(p))
    
    return p

def test_get_garden_data(mock_garden_data):
    """Testet, ob get_garden_data die korrekten Daten lädt."""
    data = garden.get_garden_data()
    assert len(data) == 2
    assert data[0]['name'] == "Monstera"
    assert data[1]['name'] == "Ficus"

def test_get_garden_data_no_file(tmp_path, monkeypatch):
    """Testet das Verhalten, wenn die Datei nicht existiert."""
    # Pfad zu einer nicht existierenden Datei
    non_existent_file = tmp_path / "non_existent.json"
    monkeypatch.setattr(garden, 'DATA_FILE', str(non_existent_file))
    
    data = garden.get_garden_data()
    assert data == []

def test_update_plant_image(mock_garden_data):
    """Testet, ob update_plant_image das Bild korrekt aktualisiert."""
    plant_id = 1
    new_image = "new_monstera.jpg"
    
    # Update durchführen
    success = garden.update_plant_image(plant_id, new_image)
    assert success is True
    
    # Überprüfen, ob die Daten im Speicher (erneutes Laden) aktualisiert wurden
    data = garden.get_garden_data()
    updated_plant = next(p for p in data if p['id'] == plant_id)
    assert updated_plant['image'] == new_image

def test_update_plant_image_invalid_id(mock_garden_data):
    """Testet update_plant_image mit einer nicht existierenden ID."""
    success = garden.update_plant_image(999, "whatever.jpg")
    assert success is False
    
    # Sicherstellen, dass nichts geändert wurde
    data = garden.get_garden_data()
    # Prüfen wir einfach das erste Element, ob es noch das alte Bild hat
    assert data[0]['image'] == "/static/images/monstera.jpg"
