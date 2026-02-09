import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Union

class Garden:
    def __init__(self):
        # self.plants structure: { "PlantName": { "fertilizer_interval_days": 30 } }
        self.plants: Dict[str, Dict] = {}
        self.fertilization_history: List[Dict] = []

    def add_plant(self, name: str, fertilizer_interval_days: int = 30):
        """
        Adds a plant to the garden with a specific fertilization interval.
        """
        if name not in self.plants:
            self.plants[name] = {
                "fertilizer_interval_days": fertilizer_interval_days
            }

    def fertilize_plant(self, plant_name: str, fertilizer_name: str, amount: float, date: str = None):
        """
        Records a fertilization event.
        """
        if plant_name not in self.plants:
            raise ValueError(f"Plant '{plant_name}' not found in garden.")
        
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")

        # Validate date format
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Date must be in YYYY-MM-DD format")

        record = {
            "plant": plant_name,
            "fertilizer": fertilizer_name,
            "amount": amount,
            "date": date
        }
        self.fertilization_history.append(record)

    def get_fertilization_history(self, plant_name: str = None) -> List[Dict]:
        """
        Returns the fertilization history, optionally filtered by plant name.
        """
        if plant_name:
            return [record for record in self.fertilization_history if record["plant"] == plant_name]
        return self.fertilization_history

    def needs_fertilizer(self, plant_name: str) -> bool:
        """
        Determines if a plant needs fertilizer based on its interval and last fertilization date.
        """
        if plant_name not in self.plants:
            raise ValueError(f"Plant '{plant_name}' not found in garden.")

        history = self.get_fertilization_history(plant_name)
        if not history:
            return True # Never fertilized, so it needs it.

        # Sort history by date descending to get the last one
        history.sort(key=lambda x: datetime.strptime(x['date'], "%Y-%m-%d"), reverse=True)
        last_fertilized_str = history[0]['date']
        last_fertilized_date = datetime.strptime(last_fertilized_str, "%Y-%m-%d")
        
        interval = self.plants[plant_name].get("fertilizer_interval_days", 30)
        next_due_date = last_fertilized_date + timedelta(days=interval)
        
        return datetime.now() >= next_due_date

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
                # Handle migration from old list format if necessary, though we assume new format for now
                loaded_plants = data.get("plants", {})
                if isinstance(loaded_plants, list):
                    # Convert old list format to dict
                    self.plants = {name: {"fertilizer_interval_days": 30} for name in loaded_plants}
                else:
                    self.plants = loaded_plants
                
                self.fertilization_history = data.get("fertilization_history", [])
        except FileNotFoundError:
            pass
