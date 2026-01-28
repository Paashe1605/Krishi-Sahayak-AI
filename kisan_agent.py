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
        # Handle dict/list inputs gracefully to prevent crashes
        if isinstance(text, (dict, list)): return str(text)
        
        clean = re.sub(r'\*\*|__', '', text) 
        clean = re.sub(r'#+', '', clean)
        clean = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', clean) # Remove links
        clean = re.sub(r'^\*\s', '• ', clean, flags=re.MULTILINE) 
        return clean.strip()

    def extract_json_with_brace_counting(self, text):
        """
        Surgically extracts the first valid JSON object using brace counting.
        This ignores intro text, citations, and markdown wrapping.
        """
        try:
            start_index = text.find('{')
            if start_index == -1: return None
            
            count = 0
            for i in range(start_index, len(text)):
                if text[i] == '{':
                    count += 1
                elif text[i] == '}':
                    count -= 1
                    # When count hits zero, we found the matching closing brace
                    if count == 0:
                        json_candidate = text[start_index:i+1]
                        return json.loads(json_candidate)
            return None
        except Exception:
            return None

    def clean_json_output(self, raw_text):
        """
        Sanitizer: Removes Search Citations and parses JSON.
        """
        if not raw_text: return None
        try:
            # 1. Remove Google Search Citations like [1], [Source]
            text = re.sub(r'\[\d+\]', '', raw_text)
            text = re.sub(r'【.*?】', '', text)
            
            # 2. Try the Surgical Brace Counter Method (Most Robust)
            extracted_data = self.extract_json_with_brace_counting(text)
            if extracted_data:
                return extracted_data

            # 3. Fallback: Classic Regex (if brace counting fails for some reason)
            text = re.sub(r'```json\s*', '', text)
            text = re.sub(r'```\s*', '', text)
            
            start = text.find('{')
            end = text.rfind('}') + 1
            if start != -1 and end != -1:
                json_str = text[start:end]
                # Fix common trailing comma errors
                json_str = re.sub(r',\s*}', '}', json_str)
                return json.loads(json_str)
            
            return json.loads(text)
        except Exception as e:
            print(f"⚠️ JSON Parse Error: {e}")
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
        config_args = {'temperature': 0.3} # Lower temp for more stable JSON
        if use_search:
            config_args['tools'] = [types.Tool(google_search=types.GoogleSearch())]
        else:
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

            # --- MASTER PROMPT ---
            master_prompt = f"""
            You are 'KisanMitra', an expert Forensic Plant Pathologist and Agricultural Market Analyst as well as an experianced Agronomist who provides best relevent results.
            
            User Query: "{user_query}"
            Language: {language}
            Location: {location}
            
            TASK:
            1. **Forensic Diagnosis:** Identify crop, disease, pathogen lifecycle, and specific visual symptoms accurately, precisely and properly.
            2. **Cures:** Provide multiple (Minimum 3) disease specific Organic (Priority, Compulsary) and Chemical remedies.
            3. **Local Intelligence:** Provide realistic details for KVK/Agri Officers, Plant Pathologists, Major Agrochemical & Crop Protection Companies in all villages, districts, and cities in {location}.
            4. **Market Analysis:** Properly compare Costs vs Risk with accuracy and figures.
            
            CRITICAL JSON RULES (Do NOT remove these or the app will crash):
            - Return ONLY a valid JSON object. No intro text.
            - **Enclose ALL KEYS and ALL VALUES in double quotes.** - Correct: "health_score": "85"
              - Wrong: "health_score": 85
            - Translate ALL strings to {language}.
            
            JSON Structure:
            {{
                "diagnosis": "Detailed diagnosis in proper point wise format {language}. Include Symptoms and best organic & chemical remedies {language}.",
                "audio_script": "Best possible proper conversational summary. Also refer user (farmer) to see the related Youtube Video and Expert Section in the below sections and recommend them to use organic remidies provided in below section for sutainability. (Max 3 sentences, begin with proper salutation, with proper speech continutity) in {language}.",
                "stats": {{ 
                    "health_score": "Integer 0-100 (as string)", 
                    "infection_severity": "Low/Medium/High (Translated string)", 
                    "confidence": "Integer 0-100 (as string)" 
                }},
                "remedies_video_queries": ["Query 1", "Query 2", "Query 3", "Query 4", "Query 5", "Query 6"],
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

            # --- ATTEMPT 1: SEARCH MODE ---
            print("🔍 Attempting Analysis WITH Google Search...")
            try:
                search_instruction = master_prompt + " \n\nIMPORTANT: Use Google Search for accurate and relevant real-time data. Do NOT include citation markers like [1] in the JSON output."
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

            # --- ATTEMPT 2: FALLBACK MODE ---
            print("🔄 Retrying WITHOUT Search (Standard Analysis)...")
            fallback_instruction = master_prompt + " \n\nUse your internal expert knowledge base."
            raw_text = self._call_ai_model(fallback_instruction, pil_image, use_search=False)
            
            data = self.clean_json_output(raw_text)
            if data:
                data['diagnosis'] = self.clean_text(data.get('diagnosis', ''))
                return data
            
            return self.get_fallback_data("Both Search and Standard analysis failed to generate valid JSON.")

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