import pytest
import os
from garden import Garden

@pytest.fixture
def garden():
    return Garden()

def test_add_plant(garden):
    garden.add_plant("Rose")
    assert "Rose" in garden.plants
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

def test_persistence(garden, tmp_path):
    file_path = tmp_path / "garden_data.json"
    garden.add_plant("Cactus")
    garden.fertilize_plant("Cactus", "DesertMix", 5)
    
    garden.save_to_file(str(file_path))
    
    new_garden = Garden()
    new_garden.load_from_file(str(file_path))
    
    assert "Cactus" in new_garden.plants
    assert len(new_garden.get_fertilization_history()) == 1
    assert new_garden.get_fertilization_history()[0]["fertilizer"] == "DesertMix"
