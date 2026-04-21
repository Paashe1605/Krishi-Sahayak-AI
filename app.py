import os
import uuid
import json
from flask import Flask, render_template, request, jsonify, url_for
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

from models import db, Diagnosis
from kisan_agent import KisanShayakAgent
from pashu_agent import PashuSahayakAgent
from rakshak_agent import KrishiRakshakAgent

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'kisan-mitra-hackathon-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///kisanmitra.db'
app.config['UPLOAD_FOLDER'] = 'static/uploads'

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('static/audio', exist_ok=True)

db.init_app(app)

with app.app_context():
    db.create_all()

agent = None
pashu_agent = None
rakshak_agent = None
try:
    project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
    location = os.getenv('GOOGLE_CLOUD_LOCATION')
    agent = KisanShayakAgent(project_id, location)
    print("✅ KisanShayak Agent is Active (Vertex AI)")
    pashu_agent = PashuSahayakAgent(project_id, location)
    print("✅ PashuSahayak Agent is Active")
    rakshak_agent = KrishiRakshakAgent(project_id, location)
    print("✅ KrishiRakshak Agent is Active")
except Exception as e:
    print(f"⚠️ Agent Offline: {e}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/kisan')
def kisan():
    return render_template('kisan_index.html')

@app.route('/pashu')
def pashu():
    return render_template('pashu_index.html')

@app.route('/rakshak')
def rakshak():
    return render_template('rakshak_index.html')

@app.route('/weather')
def weather():
    return render_template('coming_soon.html', title="Dharti Chakra")

@app.route('/diagnose', methods=['POST'])
def diagnose():
    if 'image' not in request.files: return jsonify({'error': 'No image provided'}), 400
    file = request.files['image']
    user_query = request.form.get('query', '')
    language = request.form.get('language', 'Hindi')
    location = request.form.get('location', 'India') 
    lat = request.form.get('lat')
    lng = request.form.get('lng')

    if file.filename == '': return jsonify({'error': 'No file selected'}), 400

    if file:
        filename = secure_filename(f"{uuid.uuid4().hex[:8]}_{file.filename}")
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        if not agent: return jsonify({'error': 'AI Agent is offline'}), 500

        analysis_data = agent.analyze_crop(filepath, user_query, language, location, lat, lng)
        
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
    
    return render_template('kisan_result.html', diagnosis=diagnosis_record, data=data)

@app.route('/diagnose_pashu', methods=['POST'])
def diagnose_pashu():
    if 'image' not in request.files: return jsonify({'error': 'No image provided'}), 400
    file = request.files['image']
    user_query = request.form.get('query', '')
    language = request.form.get('language', 'Hindi')
    location = request.form.get('location', 'India') 
    lat = request.form.get('lat')
    lng = request.form.get('lng')

    if file.filename == '': return jsonify({'error': 'No file selected'}), 400

    if file:
        filename = secure_filename(f"{uuid.uuid4().hex[:8]}_{file.filename}")
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        if not pashu_agent: return jsonify({'error': 'Pashu AI Agent is offline'}), 500

        analysis_data = pashu_agent.analyze_cattle(filepath, user_query, language, location, lat, lng)
        
        audio_text = analysis_data.get('audio_script', 'Diagnosis complete.')
        audio_url = pashu_agent.generate_audio(audio_text, language)

        new_diagnosis = Diagnosis(
            image_filename=filename,
            user_query=user_query,
            ai_diagnosis=json.dumps(analysis_data), 
            audio_path=audio_url
        )
        db.session.add(new_diagnosis)
        db.session.commit()

        return jsonify({'status': 'success', 'redirect_url': url_for('show_pashu_result', result_id=new_diagnosis.id)})

@app.route('/pashu_result/<int:result_id>')
def show_pashu_result(result_id):
    diagnosis_record = db.session.get(Diagnosis, result_id)
    if not diagnosis_record: return "Diagnosis not found", 404
    try:
        data = json.loads(diagnosis_record.ai_diagnosis)
    except:
        data = { "diagnosis": "Error loading data", "stats": {"health_score":0}, "products": [], "expert_contacts": [], "cost_risk_analysis": {} }
    
    return render_template('pashu_result.html', diagnosis=diagnosis_record, data=data)

@app.route('/diagnose_rakshak', methods=['POST'])
def diagnose_rakshak():
    if 'image' not in request.files: return jsonify({'error': 'No file provided'}), 400
    file = request.files['image']
    language = request.form.get('language', 'Hindi')
    location = request.form.get('location', 'India') 
    lat = request.form.get('lat')
    lng = request.form.get('lng')

    if file.filename == '': return jsonify({'error': 'No file selected'}), 400

    if file:
        filename = secure_filename(f"{uuid.uuid4().hex[:8]}_{file.filename}")
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        if not rakshak_agent: return jsonify({'error': 'Rakshak AI Agent is offline'}), 500

        analysis_data = rakshak_agent.analyze_financial(filepath, language, location, lat, lng)
        
        audio_text = analysis_data.get('audio_script', 'Analysis complete.')
        audio_url = rakshak_agent.generate_audio(audio_text, language)

        new_diagnosis = Diagnosis(
            image_filename=filename,
            user_query="Financial Report Analysis",
            ai_diagnosis=json.dumps(analysis_data), 
            audio_path=audio_url
        )
        db.session.add(new_diagnosis)
        db.session.commit()

        return jsonify({'status': 'success', 'redirect_url': url_for('show_rakshak_result', result_id=new_diagnosis.id)})

@app.route('/rakshak_result/<int:result_id>')
def show_rakshak_result(result_id):
    diagnosis_record = db.session.get(Diagnosis, result_id)
    if not diagnosis_record: return "Diagnosis not found", 404
    try:
        data = json.loads(diagnosis_record.ai_diagnosis)
    except:
        data = { "impact_summary": {"risk_level": "Unknown"}, "stats": {"financial_health_score":0}, "insurance_schemes": [], "expert_contacts": [] }
    
    return render_template('rakshak_result.html', diagnosis=diagnosis_record, data=data)

if __name__ == '__main__':
    with app.app_context(): db.create_all()
    app.run(debug=True, port=5000)

    # © 2026 Paaras Shemrudkar & Prachi Sharma (Owners of KisanMitra AI). All rights reserved.