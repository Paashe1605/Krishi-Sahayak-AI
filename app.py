import os
import uuid
import json
from flask import Flask, render_template, request, jsonify, url_for
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

from models import db, Diagnosis
from kisan_agent import KisanMitraAgent

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'kisan-mitra-hackathon-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///kisanmitra.db'
app.config['UPLOAD_FOLDER'] = 'static/uploads'

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('static/audio', exist_ok=True)

db.init_app(app)

agent = None
try:
    project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
    location = os.getenv('GOOGLE_CLOUD_LOCATION')
    agent = KisanMitraAgent(project_id, location)
    print("✅ KisanMitra Agent is Active (Vertex AI)")
except Exception as e:
    print(f"⚠️ Agent Offline: {e}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/diagnose', methods=['POST'])
def diagnose():
    if 'image' not in request.files: return jsonify({'error': 'No image provided'}), 400
    file = request.files['image']
    user_query = request.form.get('query', '')
    language = request.form.get('language', 'Hindi')
    location = request.form.get('location', 'India') 

    if file.filename == '': return jsonify({'error': 'No file selected'}), 400

    if file:
        filename = secure_filename(f"{uuid.uuid4().hex[:8]}_{file.filename}")
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        if not agent: return jsonify({'error': 'AI Agent is offline'}), 500

        analysis_data = agent.analyze_crop(filepath, user_query, language, location)
        
        audio_text = analysis_data.get('audio_script', 'Diagnosis complete.')
        audio_url = agent.generate_audio(audio_text, language)

        new_diagnosis = Diagnosis(
            image_filename=filename,
            user_query=user_query,
            ai_diagnosis=json.dumps(analysis_data), 
            audio_path=audio_url
        )
        db.session.add(new_diagnosis)
        db.session.commit()

        return jsonify({'status': 'success', 'redirect_url': url_for('show_result', result_id=new_diagnosis.id)})

@app.route('/result/<int:result_id>')
def show_result(result_id):
    diagnosis_record = db.session.get(Diagnosis, result_id)
    if not diagnosis_record: return "Diagnosis not found", 404
    try:
        data = json.loads(diagnosis_record.ai_diagnosis)
    except:
        data = { "diagnosis": "Error loading data", "stats": {"health_score":0}, "products": [], "expert_contacts": [], "cost_risk_analysis": {} }
    
    return render_template('result.html', diagnosis=diagnosis_record, data=data)

if __name__ == '__main__':
    with app.app_context(): db.create_all()
    app.run(debug=True, port=5000)