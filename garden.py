import json
from datetime import datetime
from typing import List, Dict, Optional

class Garden:
    def __init__(self):
        self.plants: List[str] = []
        self.fertilization_history: List[Dict] = []

    def add_plant(self, name: str):
        if name not in self.plants:
            self.plants.append(name)

    def fertilize_plant(self, plant_name: str, fertilizer_name: str, amount: float, date: str = None):
        if plant_name not in self.plants:
            raise ValueError(f"Plant '{plant_name}' not found in garden.")
        
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")

        record = {
            "plant": plant_name,
            "fertilizer": fertilizer_name,
            "amount": amount,
            "date": date
        }
        self.fertilization_history.append(record)

    def get_fertilization_history(self, plant_name: str = None) -> List[Dict]:
        if plant_name:
            return [record for record in self.fertilization_history if record["plant"] == plant_name]
        return self.fertilization_history

    def save_to_file(self, filepath: str):
        data = {
            "plants": self.plants,
            "fertilization_history": self.fertilization_history
        }
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=4)

    def load_from_file(self, filepath: str):
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
                self.plants = data.get("plants", [])
                self.fertilization_history = data.get("fertilization_history", [])
        except FileNotFoundError:
            pass  # Start with empty garden if file doesn't exist
