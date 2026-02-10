import pytest
import os
from datetime import datetime, timedelta
from garden import Garden

@pytest.fixture
def garden():
    return Garden()

def test_add_plant(garden):
    garden.add_plant("Rose", fertilizer_interval_days=14)
    assert "Rose" in garden.plants
    assert garden.plants["Rose"]["fertilizer_interval_days"] == 14
    assert len(garden.plants) == 1

def test_fertilize_plant(garden):
    garden.add_plant("Tomato")
    garden.fertilize_plant("Tomato", "NPK 10-10-10", 50.0, "2023-10-27")
    
    history = garden.get_fertilization_history()
    assert len(history) == 1
    assert history[0]["plant"] == "Tomato"
    assert history[0]["fertilizer"] == "NPK 10-10-10"
    assert history[0]["amount"] == 50.0
    assert history[0]["date"] == "2023-10-27"

def test_fertilize_plant_unknown(garden):
    with pytest.raises(ValueError):
        garden.fertilize_plant("Unknown", "Water", 10)

def test_history_filter(garden):
    garden.add_plant("Rose")
    garden.add_plant("Tulip")
    
    garden.fertilize_plant("Rose", "A", 10)
    garden.fertilize_plant("Tulip", "B", 20)
    garden.fertilize_plant("Rose", "A", 15)
    
    rose_history = garden.get_fertilization_history("Rose")
    assert len(rose_history) == 2
    for record in rose_history:
        assert record["plant"] == "Rose"

def test_needs_fertilizer(garden):
    # Case 1: Never fertilized
    garden.add_plant("NewPlant", fertilizer_interval_days=30)
    assert garden.needs_fertilizer("NewPlant") is True
    
    # Case 2: Fertilized recently
    garden.add_plant("FreshPlant", fertilizer_interval_days=30)
    today = datetime.now().strftime("%Y-%m-%d")
    garden.fertilize_plant("FreshPlant", "Mix", 5, date=today)
    assert garden.needs_fertilizer("FreshPlant") is False
    
    # Case 3: Fertilized long ago
    garden.add_plant("OldPlant", fertilizer_interval_days=30)
    past_date = (datetime.now() - timedelta(days=31)).strftime("%Y-%m-%d")
    garden.fertilize_plant("OldPlant", "Mix", 5, date=past_date)
    assert garden.needs_fertilizer("OldPlant") is True

def test_persistence(garden, tmp_path):
    file_path = tmp_path / "garden_data.json"
    garden.add_plant("Cactus", fertilizer_interval_days=45)
    garden.fertilize_plant("Cactus", "DesertMix", 5)
    
    garden.save_to_file(str(file_path))
    
    new_garden = Garden()
    new_garden.load_from_file(str(file_path))
    
    assert "Cactus" in new_garden.plants
    assert new_garden.plants["Cactus"]["fertilizer_interval_days"] == 45
    assert len(new_garden.get_fertilization_history()) == 1
    assert new_garden.get_fertilization_history()[0]["fertilizer"] == "DesertMix"
