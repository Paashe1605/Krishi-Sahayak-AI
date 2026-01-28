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
        """Cleans text for TTS and Display (removes markdown)."""
        if not text: return ""
        # Handle dict/list inputs gracefully
        if isinstance(text, (dict, list)): return str(text)
        
        clean = re.sub(r'\*\*|__', '', text) 
        clean = re.sub(r'#+', '', clean)
        clean = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', clean) # Remove links
        clean = re.sub(r'^\*\s', '• ', clean, flags=re.MULTILINE) 
        return clean.strip()

    def clean_json_output(self, raw_text):
        """
        The 'Sanitizer': Removes Search Citations and extracts JSON.
        """
        if not raw_text: return None
        try:
            # 1. Remove Google Search Citations like [1], [2], 【1:0†source】
            # This is the key fix for the "Expecting value" error
            text = re.sub(r'\[\d+\]', '', raw_text)
            text = re.sub(r'【.*?】', '', text)
            
            # 2. Remove code block markers
            text = re.sub(r'```json\s*', '', text)
            text = re.sub(r'```\s*', '', text)
            
            # 3. Find the largest JSON block { ... }
            start = text.find('{')
            end = text.rfind('}') + 1
            if start != -1 and end != -1:
                json_str = text[start:end]
                # Fix common trailing comma errors
                json_str = re.sub(r',\s*}', '}', json_str)
                return json.loads(json_str)
            
            # 4. Try parsing the whole text
            return json.loads(text)
        except Exception as e:
            print(f"⚠️ JSON Parse Error: {e}")
            # print(f"DEBUG RAW TEXT: {raw_text}") # Uncomment for deeper debugging
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
        config_args = {'temperature': 0.4}
        if use_search:
            config_args['tools'] = [types.Tool(google_search=types.GoogleSearch())]
        else:
            # Enforce JSON mode ONLY when not searching to avoid conflicts
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

            # --- MASTER PROMPT (Used for BOTH Search & Fallback) ---
            # This ensures the Fallback is just as "Top-Notch" as the Search version.
            master_prompt = f"""
            You are 'KisanMitra', an expert Forensic Plant Pathologist, Agronomist, and Market Analyst.
            
            User Query: "{user_query}"
            Language: {language}
            User Location: {location}
            
            TASK:
            1. **Forensic Diagnosis:** Identify crop, disease, lifecycle, and specific visual symptoms. Be extremely detailed.
            2. **Cures:** Provide 4+ specific remedies (Organic & Chemical).
            3. **Local Intelligence:** Provide realistic KVK/Agri Officer contacts for {location}.
            4. **Market Analysis:** Compare Costs vs Risk with estimated figures.
            
            CRITICAL OUTPUT RULES:
            - Return ONLY a valid JSON object.
            - Translate ALL strings to {language}.
            - Translate Numbers (e.g., "50%" -> "५०%").
            
            JSON Structure:
            {{
                "diagnosis": "Detailed point-wise diagnosis in {language}.",
                "audio_script": "Conversational summary in {language} (max 3 sentences).",
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

            # --- ATTEMPT 1: SEARCH MODE (Real-Time Data) ---
            print("🔍 Attempting Analysis WITH Google Search...")
            try:
                # We specifically instruct to avoid citation markers in the JSON
                search_instruction = master_prompt + " \n\nIMPORTANT: Use Google Search to find real-time prices and contacts. Do NOT include citation markers like [1] or sources in the JSON output."
                
                raw_text = self._call_ai_model(search_instruction, pil_image, use_search=True)
                data = self.clean_json_output(raw_text)
                
                if data and "diagnosis" in data:
                    print("✅ Search Analysis Successful.")
                    data['diagnosis'] = self.clean_text(data.get('diagnosis', ''))
                    return data
                else:
                    print("⚠️ Search output format invalid. Switching to Fallback...")
            except Exception as e:
                print(f"⚠️ Search failed ({e}). Switching to Fallback...")

            # --- ATTEMPT 2: FALLBACK MODE (Internal Knowledge) ---
            # Now uses the SAME high-quality master_prompt
            print("🔄 Retrying WITHOUT Search (Standard Analysis)...")
            
            fallback_instruction = master_prompt + " \n\nUse your internal expert knowledge base. Do not use external search."
            raw_text = self._call_ai_model(fallback_instruction, pil_image, use_search=False)
            
            data = self.clean_json_output(raw_text)
            if data:
                data['diagnosis'] = self.clean_text(data.get('diagnosis', ''))
                return data
            
            return self.get_fallback_data("Both Search and Standard analysis failed.")

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