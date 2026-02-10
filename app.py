from flask import Flask, render_template, request, jsonify
from garden import get_garden_data, update_plant_image
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Konfiguration für Uploads
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Sicherstellen, dass der Upload-Ordner existiert
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    # Prüfen, ob Admin-Modus aktiviert ist (?admin=true)
    is_admin = request.args.get('admin') == 'true'
    
    # Daten aus garden.py abrufen
    plants = get_garden_data()
    
    # Template rendern und Daten übergeben
    return render_template('index.html', plants=plants, is_admin=is_admin)

@app.route('/upload/<int:plant_id>', methods=['POST'])
def upload_file(plant_id):
    if 'image' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['image']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
        
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Eindeutigen Dateinamen generieren: ID_Originalname
        save_name = f"{plant_id}_{filename}"
        
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], save_name)
        file.save(filepath)
        
        # Pfad für das Frontend (relativ zum Web-Root)
        web_path = f"/static/uploads/{save_name}"
        
        # Datenbank aktualisieren
        update_plant_image(plant_id, web_path)
        
        return jsonify({'success': True, 'new_path': web_path})
    
    return jsonify({'error': 'File type not allowed'}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5000)
