import os
import uuid
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

# Import our custom modules
from models import db, Diagnosis
from kisan_agent import KisanMitraAgent

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'kisan-mitra-hackathon-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///kisanmitra.db'
app.config['UPLOAD_FOLDER'] = 'static/uploads'

# Ensure folders exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('static/audio', exist_ok=True)

db.init_app(app)

# Initialize Agent
agent = None
try:
    api_key = os.getenv('GEMINI_API_KEY')
    agent = KisanMitraAgent(api_key)
    print("✅ KisanMitra Agent is Active")
except Exception as e:
    print(f"⚠️ Agent Offline: {e}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/diagnose', methods=['POST'])
def diagnose():
    """
    Handles the form submission: Image + Text/Voice Query
    """
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400
    
    file = request.files['image']
    user_query = request.form.get('query', '') # The text (typed or voice-converted)
    language = request.form.get('language', 'Hindi')

    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if file:
        # 1. Save the Image
        filename = secure_filename(f"{uuid.uuid4().hex[:8]}_{file.filename}")
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # 2. Ask the Agent
        if not agent:
            return jsonify({'error': 'AI Agent is not configured correctly.'}), 500

        # Get Text Diagnosis
        diagnosis_text = agent.analyze_crop(filepath, user_query, language)

        # Get Audio Version
        audio_url = agent.generate_audio(diagnosis_text, language)

        return jsonify({
            'status': 'success',
            'diagnosis': diagnosis_text,
            'audio_url': audio_url,
            'image_url': f"/static/uploads/{filename}"
        })

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)