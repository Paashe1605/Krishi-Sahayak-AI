import os
import uuid
import json
import re
from google import genai
from PIL import Image
from gtts import gTTS

class KisanMitraAgent:
    def __init__(self, project_id, location):
        if not project_id or not location:
            raise ValueError("GCP Project ID or Location is missing.")
        
        print(f"🔄 Connecting to Vertex AI (Project: {project_id}, Region: {location})...")
        try:
            self.client = genai.Client(
                vertexai=True, 
                project=project_id, 
                location=location
            )
            self.model_name = "gemini-2.5-flash"
            print(f"✅ KisanMitra Agent initialized using: {self.model_name}")
            
        except Exception as e:
            print(f"❌ Failed to initialize Vertex AI Client: {e}")
            raise e

    def clean_text(self, text):
        """Removes markdown asterisks, hashes, and formatting artifacts."""
        if not text: return ""
        # Remove **bold**, *italic*, # Headers, and markdown links
        clean = re.sub(r'\*\*|__', '', text) 
        clean = re.sub(r'#+', '', clean)
        clean = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', clean) # Remove markdown links but keep text
        clean = re.sub(r'^\*\s', '• ', clean, flags=re.MULTILINE) # Convert bullets
        return clean.strip()

    def analyze_crop(self, image_path, user_query=None, language="Hindi"):
        try:
            pil_image = Image.open(image_path)
            
            if not user_query:
                user_query = "What is wrong with my plant?"

            # --- JSON STRUCTURED PROMPT ---
            prompt = f"""
            You are 'KisanMitra', an expert Agronomist.
            User Query: "{user_query}"
            Language: {language}
            
            Analyze the image and return a VALID JSON object. 
            DO NOT use Markdown formatting (no asterisks **, no hashes #).
            
            The JSON structure must be:
            {{
                "diagnosis": "Detailed diagnosis text here (Plain text only). Include disease name, cause, and organic/chemical solutions.",
                "audio_script": "A short, warm, conversational summary for text-to-speech (max 2 sentences).",
                "stats": {{
                    "health_score": (integer 0-100, where 100 is healthy),
                    "infection_severity": "Low/Medium/High",
                    "confidence": (integer 0-100)
                }},
                "remedies_video_queries": [
                    "String for YouTube search 1 (e.g. 'How to cure Tomato Blight organic')",
                    "String for YouTube search 2"
                ],
                "products": [
                    {{ "name": "Name of specific chemical/product", "type": "Chemical/Organic" }}
                ]
            }}
            
            Ensure the response is ONLY the JSON object.
            """

            # Request JSON response type from Gemini
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[prompt, pil_image],
                config={'response_mime_type': 'application/json'} 
            )
            
            raw_text = response.text if response else "{}"
            
            # Sanitize response just in case
            raw_text = raw_text.replace("```json", "").replace("```", "")
            
            try:
                data = json.loads(raw_text)
                
                # Double clean the text fields to ensure no asterisks slip through
                data['diagnosis'] = self.clean_text(data.get('diagnosis', 'Could not diagnose.'))
                return data
            except json.JSONDecodeError:
                # Fallback if AI fails to give JSON
                return {
                    "diagnosis": self.clean_text(raw_text),
                    "audio_script": "Error in processing data.",
                    "stats": {"health_score": 0, "infection_severity": "Unknown", "confidence": 0},
                    "remedies_video_queries": [],
                    "products": []
                }

        except Exception as e:
            print(f"Analysis Error: {e}")
            return {
                "diagnosis": f"Error: {str(e)}", 
                "audio_script": "An error occurred.",
                "stats": {}, 
                "remedies_video_queries": [], 
                "products": []
            }

    def generate_audio(self, text, language="Hindi"):
        try:
            lang_codes = {'Hindi': 'hi', 'English': 'en', 'Marathi': 'mr', 'Tamil': 'ta'}
            code = lang_codes.get(language, 'hi')
            
            # Ensure we don't speak weird symbols
            clean_text = self.clean_text(text) 
            
            tts = gTTS(text=clean_text, lang=code, slow=False)
            filename = f"response_{uuid.uuid4().hex[:8]}.mp3"
            save_path = os.path.join("static", "audio", filename)
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            tts.save(save_path)
            return f"/static/audio/{filename}"
        except Exception as e:
            print(f"Audio Error: {e}")
            return None