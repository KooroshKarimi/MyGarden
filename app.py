from flask import Flask, render_template
from garden import Garden
import os

app = Flask(__name__)

# Initialize Garden
garden = Garden()

# Path to data file
DATA_FILE = 'garden_data.json'

# Load existing data if available
if os.path.exists(DATA_FILE):
    garden.load_from_file(DATA_FILE)

# If no plants exist (first run), add demo data
if not garden.plants:
    demo_plants = [
        ("Monstera Deliciosa", 14),
        ("Ficus Lyrata", 30),
        ("Sansevieria", 60),
        ("Calathea Orbifolia", 21),
        ("Pilea Peperomioides", 14),
        ("Yucca Palm", 45)
    ]
    for name, interval in demo_plants:
        garden.add_plant(name, fertilizer_interval_days=interval)
    
    # Save demo data
    garden.save_to_file(DATA_FILE)

@app.route('/')
def index():
    plants_list = []
    
    # Iterate over plants to prepare view data
    for name, details in garden.plants.items():
        needs_fert = garden.needs_fertilizer(name)
        interval = details.get('fertilizer_interval_days', 30)
        
        # Mock Water Needs (since not in backend yet)
        # Deterministic mock based on name length
        water_levels = ["Wenig Wasser", "Mäßig Wasser", "Viel Wasser"]
        water_needs = water_levels[len(name) % 3]

        plants_list.append({
            "name": name,
            "needs_fertilizer": needs_fert,
            "status_text": "DÜNGEN" if needs_fert else "OK",
            "water_needs": water_needs,
            "interval": interval
        })

    return render_template('index.html', plants=plants_list)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
