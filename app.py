from flask import Flask, render_template
from garden import get_garden_data

app = Flask(__name__)

@app.route('/')
def index():
    # Daten aus garden.py abrufen
    plants = get_garden_data()
    # Template rendern und Daten übergeben
    return render_template('index.html', plants=plants)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
