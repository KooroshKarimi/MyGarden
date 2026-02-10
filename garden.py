
def get_garden_data():
    """
    Gibt eine Liste von Pflanzen-Dictionaries zurück.
    Simuliert eine Datenbankabfrage.
    """
    return [
        {
            "id": 1,
            "name": "Monstera Deliciosa",
            "scientific_name": "Monstera deliciosa",
            "status": "Gedeiht",
            "water_needs": "Mittel",
            "location": "Wohnzimmer",
            "image": "https://images.unsplash.com/photo-1614594975525-e45190c55d0b?auto=format&fit=crop&q=80&w=600"
        },
        {
            "id": 2,
            "name": "Geigenfeige",
            "scientific_name": "Ficus lyrata",
            "status": "Braucht Wasser",
            "water_needs": "Hoch",
            "location": "Flur",
            "image": "https://images.unsplash.com/photo-1612361619628-6695d999b3e2?auto=format&fit=crop&q=80&w=600"
        },
        {
            "id": 3,
            "name": "Bogenhanf",
            "scientific_name": "Sansevieria",
            "status": "Robust",
            "water_needs": "Niedrig",
            "location": "Schlafzimmer",
            "image": "https://images.unsplash.com/photo-1598880940371-c756e015fea1?auto=format&fit=crop&q=80&w=600"
        },
        {
            "id": 4,
            "name": "Efeutute",
            "scientific_name": "Epipremnum aureum",
            "status": "Wächst schnell",
            "water_needs": "Mittel",
            "location": "Küche",
            "image": "https://images.unsplash.com/photo-1596547609652-9cf5d8d76921?auto=format&fit=crop&q=80&w=600"
        },
        {
            "id": 5,
            "name": "Korbmarante",
            "scientific_name": "Calathea",
            "status": "Empfindlich",
            "water_needs": "Hoch",
            "location": "Bad",
            "image": "https://images.unsplash.com/photo-1620126960868-627769240943?auto=format&fit=crop&q=80&w=600"
        },
        {
            "id": 6,
            "name": "Gummibaum",
            "scientific_name": "Ficus elastica",
            "status": "Ruhephase",
            "water_needs": "Niedrig",
            "location": "Büro",
            "image": "https://images.unsplash.com/photo-1596547610277-243fef51785d?auto=format&fit=crop&q=80&w=600"
        }
    ]
