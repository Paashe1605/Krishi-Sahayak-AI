import os
import uuid
import json
import re
import asyncio
from google import genai
from google.genai import types
from PIL import Image
from gtts import gTTS
import edge_tts

# --- Helper to run async EdgeTTS in sync code ---
def run_async_tts(coro):
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            return asyncio.run_coroutine_threadsafe(coro, loop).result()
        else:
            return loop.run_until_complete(coro)
    except RuntimeError:
        return asyncio.run(coro)

class KisanMitraAgent:
    def __init__(self, project_id, location):
        if not project_id or not location:
            raise ValueError("GCP Project ID or Location is missing.")
        
        print(f"🔄 Connecting to Vertex AI (Project: {project_id}, Region: {location})...")
        try:
            self.client = genai.Client(vertexai=True, project=project_id, location=location)
            self.model_name = "gemini-2.5-flash"
            print(f"✅ KisanMitra Agent initialized using: {self.model_name}")
        except Exception as e:
            print(f"❌ Failed to initialize Vertex AI Client: {e}")
            raise e

    def clean_text(self, text):
        if not text: return ""
        clean = re.sub(r'\*\*|__', '', text) 
        clean = re.sub(r'#+', '', clean)
        clean = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', clean)
        clean = re.sub(r'^\*\s', '• ', clean, flags=re.MULTILINE) 
        return clean.strip()

    def clean_json_output(self, raw_text):
        """
        Robustly extracts JSON, handling comments and markdown artifacts.
        """
        if not raw_text: return None
        try:
            # 1. Remove code block markers
            text = re.sub(r'```json\s*', '', raw_text)
            text = re.sub(r'```\s*', '', text)
            
            # 2. Remove C++ style comments // which break JSON parsers
            text = re.sub(r'//.*', '', text)
            
            # 3. Find the first { and the last }
            start = text.find('{')
            end = text.rfind('}') + 1
            if start != -1 and end != -1:
                json_str = text[start:end]
                return json.loads(json_str)
            
            return None
        except Exception as e:
            print(f"⚠️ JSON Parse Error: {e}")
            # print(f"📄 Raw Text causing error: {raw_text}") # Uncomment to debug
            return None

    def get_fallback_data(self, error_msg):
        return {
            "diagnosis": f"⚠️ Analysis error: {error_msg}. Please try again.",
            "audio_script": "An error occurred.",
            "stats": { "health_score": 0, "infection_severity": "Error", "confidence": 0 },
            "remedies_video_queries": [],
            "products": [],
            "expert_contacts": [],
            "cost_risk_analysis": {
                "organic": {"cost": "-", "risk": "-", "timeline": "-"},
                "chemical": {"cost": "-", "risk": "-", "timeline": "-"}
            }
        }

    def _call_ai_model(self, prompt, pil_image, use_search=False):
        """Internal helper to call AI with or without search tools."""
        config_args = {'temperature': 0.4}
        
        if use_search:
            config_args['tools'] = [types.Tool(google_search=types.GoogleSearch())]
        else:
            # Enforce JSON when not searching
            config_args['response_mime_type'] = 'application/json'

        response = self.client.models.generate_content(
            model=self.model_name,
            contents=[prompt, pil_image],
            config=types.GenerateContentConfig(**config_args)
        )
        return response.text if response else "{}"

    def analyze_crop(self, image_path, user_query=None, language="Hindi", location="India"):
        try:
            pil_image = Image.open(image_path)
            if not user_query: user_query = "What is wrong with my plant?"

            base_prompt = f"""
             You are 'KisanMitra', an expert Forensic Plant Pathologist and Agricultural Market Analyst as well as an Agronomist who provides best results.
            
            User Query: "{user_query}"
            Language: {language}
            Location: {location}
            
            TASK:
            1. **Forensic Diagnosis:** Identify crop, disease, pathogen lifecycle, and specific visual symptoms properly.
            2. **Cures:** Provide multiple(Minimum 4) disease specific Organic (Priority) and Chemical remedies.
            3. **Local Intelligence:** Provide realistic details for KVK/Agri Officers in all major villages, districts,and cities.{location}.
            4. **Market Analysis:** Properly compare Costs vs Risk with accuracy and figures.
            
            CRITICAL OUTPUT INSTRUCTION: 
            Return ONLY a valid JSON object. 
            Translate ALL strings to {language}. 
            Translate Numbers (e.g. "50%" -> "५०%", "Cost: Low" -> "लागत: कम").
            
            JSON Structure:
            {{
                "diagnosis": "Detailed diagnosis in proper point wise format {language}. Include Symptoms and best organic & chemical remedies {language}.",
                "audio_script": "Best possible proper conversational summary and also refer user(farmer) to see the related Youtube Video and Experts Contacts in the below sections in {language} (max 3 sentences)(Begin with proper salutation).",
                "stats": {{ 
                    "health_score": "Integer (0-100)", 
                    "infection_severity": "Low/Medium/High (Translated)", 
                    "confidence": "Integer (0-100)" 
                }},
                "remedies_video_queries": ["Query 1", "Query 2", "Query 3", "Query 4"],
                "products": [ 
                    {{ "name": "Organic Product Name", "type": "Organic" }},
                    {{ "name": "Chemical Product Name", "type": "Chemical" }}
                ],
                "expert_contacts": [
                    {{ "name": "KVK/Officer Name", "role": "Role", "contact": "Phone", "location": "City" }},
                    {{ "name": "Kisan Call Center", "role": "Helpline", "contact": "1800-180-1551", "location": "National" }}
                ],
                "cost_risk_analysis": {{
                    "organic": {{ "cost": "Low/Medium", "risk": "Safe", "timeline": "Weeks" }},
                    "chemical": {{ "cost": "High", "risk": "Toxic", "timeline": "Days" }}
                }}
            }}
            """

            # --- ATTEMPT 1: SEARCH ---
            print("🔍 Attempting Analysis WITH Google Search...")
            try:
                # We specifically ask NOT to include citations in the JSON to avoid breaking it
                search_prompt = base_prompt + " Use Google Search for real-time info like Use Google Search to find Products(medicines) & current market prices for medicines and actual contact numbers for KVKs and verify diagnosis. Do NOT include markdown citations or comments in the JSON."
                raw_text = self._call_ai_model(search_prompt, pil_image, use_search=True)
                
                data = self.clean_json_output(raw_text)
                if data and "diagnosis" in data:
                    print("✅ Search Analysis Successful.")
                    data['diagnosis'] = self.clean_text(data.get('diagnosis', ''))
                    return data
                else:
                    print("⚠️ Search result was not valid JSON. Falling back...")
            except Exception as e:
                print(f"⚠️ Search failed ({e}). Falling back...")

            # --- ATTEMPT 2: FALLBACK ---
            print("🔄 Retrying WITHOUT Search (Standard Analysis)...")
            fallback_prompt = base_prompt + " Use internal knowledge."
            raw_text = self._call_ai_model(fallback_prompt, pil_image, use_search=False)
            
            data = self.clean_json_output(raw_text)
            if data:
                data['diagnosis'] = self.clean_text(data.get('diagnosis', ''))
                return data
            
            return self.get_fallback_data("Analysis failed.")

        except Exception as e:
            print(f"❌ Critical Error: {e}")
            return self.get_fallback_data(str(e))

    def generate_audio(self, text, language="Hindi"):
        try:
            edge_voice_map = {
                'Hindi': 'hi-IN-SwaraNeural',
                'English': 'en-IN-NeerjaNeural',
                'Marathi': 'mr-IN-AarohiNeural',
                'Tamil': 'ta-IN-PallaviNeural',
                'Gujarati': 'gu-IN-DhwaniNeural',
                'Punjabi': 'pa-IN-OjasNeural',
                'Bengali': 'bn-IN-TanishaaNeural'
            }
            
            clean_text = self.clean_text(text)
            filename = f"response_{uuid.uuid4().hex[:8]}.mp3"
            save_path = os.path.join("static", "audio", filename)
            os.makedirs(os.path.dirname(save_path), exist_ok=True)

            if language in edge_voice_map:
                try:
                    async def _save_edge():
                        communicate = edge_tts.Communicate(clean_text, edge_voice_map[language])
                        await communicate.save(save_path)
                    run_async_tts(_save_edge())
                    return f"/static/audio/{filename}"
                except:
                    pass 

            lang_codes = {'Hindi': 'hi', 'English': 'en', 'Marathi': 'mr', 'Tamil': 'ta', 'Gujarati': 'gu', 'Punjabi': 'pa', 'Bengali': 'bn'}
            code = lang_codes.get(language, 'hi')
            tts = gTTS(text=clean_text, lang=code, slow=False)
            tts.save(save_path)
            return f"/static/audio/{filename}"

        except Exception as e:
            print(f"Audio Error: {e}")
            return None