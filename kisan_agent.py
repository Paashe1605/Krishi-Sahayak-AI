import os
import uuid
import json
import re
import edge_tts
import asyncio
from google import genai
from google.genai import types
from PIL import Image
from gtts import gTTS


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
        # Remove bolding, headers, and links for cleaner reading/TTS
        clean = re.sub(r'\*\*|__', '', text) 
        clean = re.sub(r'#+', '', clean)
        clean = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', clean)
        clean = re.sub(r'^\*\s', '• ', clean, flags=re.MULTILINE) 
        return clean.strip()

    def analyze_crop(self, image_path, user_query=None, language="Hindi"):
        try:
            pil_image = Image.open(image_path)
            if not user_query: user_query = "What is wrong with my plant?"

            prompt = f"""
            You are 'KisanMitra', an elite Agronomist and expert Forensic Plant Pathologist who provides very accurate diagnoses.
            
            User Query: "{user_query}"
            Language: {language}
            
            ***FORENSIC VISUAL PROTOCOL (Perform this internally):***
            1. SYMMETRY CHECK: Asymmetrical spots = Virus/Fungi. Symmetrical = Deficiency.
            2. VEIN CHECK: Green veins + Yellow leaf = Nutrient Deficiency.
            3. ROOT CHECK: If Wilting + Green Leaves, suspect Root Rot/Wilt (not just drought).
            
            Use the 'google_search' tool to verify if there are active disease outbreaks and latest remedies for this crop in the user's region (if known) or generally in 2025-2026.
            Use the 'google_search' tool to cross check the image, whole diagnosis and remedies with latest agricultural advisories and organic treatments.'

            TASK:
            1. Analyze the image and Search Results properly, take assistance from 'google_search' tool if needed, for accurate results.
            2. Return a VALID JSON object. DO NOT use Markdown formatting.
            3. PROVIDE CURES: Prioritize ORGANIC/HOME remedies first.
            
            The JSON structure must be:
            {{
                "diagnosis": "Start with [Plant] : [Disease]. Follow with 'Evidence:' explaining the visual logic (e.g. 'Asymmetrical spots rule out Zinc deficiency'). Then list 1. ORGANIC and 2. CHEMICAL remedies. The above response must be detailed and point wise, with proper formatting, spacing and justified, also provide the symptoms and solutions in a clear, step-by-step list format (use '•' for bullets).Make it detailed but easy to read. Highlight key points and words.",
                "audio_script": "A short, warm, conversational summary for text-to-speech (max 3 sentences). Start with proper salutation to the farmer, mention the disease and the best organic cure and optional chemical remedy.",
                "stats": {{
                    "health_score": (integer 0-100),
                    "infection_severity": "Low/Medium/High",
                    "confidence": (integer 0-100)
                }},
                "remedies_video_queries": [ "Specific YouTube search query 1", "Specific YouTube search query 2" ],
                "products": [ 
                    {{ "name": "Name of ORGANIC product (e.g. Neem Oil)", "type": "Organic" }},
                    {{ "name": "Name of ORGANIC product", "type": "Organic" }},
                    {{ "name": "Name of Chemical product", "type": "Chemical" }}
                ]
            }}
            """

            # --- FIXED CONFIGURATION ---
            # REMOVED 'response_mime_type' to fix the 400 Error.
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[prompt, pil_image],
                config=types.GenerateContentConfig(
                    tools=[types.Tool(google_search=types.GoogleSearch())],
                    temperature=0.4  # Low temperature helps keep JSON structure stable
                )
            )
            
            raw_text = response.text if response else "{}"
            
            # --- ROBUST JSON CLEANUP ---
            # The model might wrap the JSON in ```json ... ``` blocks. We must strip them.
            raw_text = raw_text.strip()
            if raw_text.startswith("```json"):
                raw_text = raw_text[7:]
            if raw_text.startswith("```"):
                raw_text = raw_text[3:]
            if raw_text.endswith("```"):
                raw_text = raw_text[:-3]
            
            raw_text = raw_text.strip() # Final trim

            try:
                data = json.loads(raw_text)
                data['diagnosis'] = self.clean_text(data.get('diagnosis', 'Could not diagnose.'))
                return data
            except json.JSONDecodeError:
                # Fallback if the model returns plain text instead of JSON
                print(f"JSON Parse Failed. Raw Text: {raw_text}")
                return { 
                    "diagnosis": self.clean_text(raw_text), 
                    "audio_script": "I could not generate a structured report, but here is my analysis.", 
                    "stats": {}, 
                    "remedies_video_queries": [], 
                    "products": [] 
                }

        except Exception as e:
            print(f"Analysis Error: {e}")
            return { "diagnosis": f"Error: {str(e)}", "audio_script": "Error.", "stats": {}, "remedies_video_queries": [], "products": [] }

   # --- ROBUST HYBRID AUDIO ENGINE (3-Layer Safety) ---
    def generate_audio(self, text, language="Hindi"):
        filename = f"response_{uuid.uuid4().hex[:8]}.mp3"
        save_path = os.path.join("static", "audio", filename)
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        clean_text = self.clean_text(text)

        # 1. Map for Edge-TTS (High Quality)
        edge_voice_map = {
            'Hindi': 'hi-IN-SwaraNeural',
            'English': 'en-IN-NeerjaNeural',
            'Marathi': 'mr-IN-AarohiNeural',
            'Tamil': 'ta-IN-PallaviNeural',
            'Gujarati': 'gu-IN-DhwaniNeural',
            'Kannada': 'kn-IN-SapnaNeural',
            'Telugu': 'te-IN-ShrutiNeural',
            'Bengali': 'bn-IN-TanishaaNeural',
            'Malayalam': 'ml-IN-SobhanaNeural',
            'Punjabi': 'pa-IN-OjasNeural',
            'Odia': 'or-IN-SubhasiniNeural'
        }

        # 2. Map for Google TTS (Standard Quality) - COVERS EVERYTHING
        gtts_code_map = {
            'Hindi': 'hi',
            'English': 'en',
            'Marathi': 'mr',
            'Tamil': 'ta',
            'Gujarati': 'gu',
            'Kannada': 'kn',
            'Telugu': 'te',
            'Bengali': 'bn',
            'Punjabi': 'pa',     # Google supports this!
            'Malayalam': 'ml',
            'Odia': 'or',         # Google supports this!
            'Assamese': 'as',     # Google supports this!
            'Kashmiri': 'ks',     # Worth trying
            'Rajasthani': 'hi'    # Fallback to Hindi
        }

        # --- Helper: Safe Async Runner ---
        def run_async_tts(coro):
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(coro)
                loop.close()
                return True
            except Exception as e:
                print(f"⚠️ Async Execution Failed: {e}")
                return False

        # --- STEP 1: Try Edge-TTS (Best Quality) ---
        if language in edge_voice_map:
            print(f"🎤 Attempting Edge-TTS for {language}...")
            async def _save_edge():
                communicate = edge_tts.Communicate(clean_text, edge_voice_map[language])
                await communicate.save(save_path)

            # If successful, return file. If fails, proceed to Step 2.
            if run_async_tts(_save_edge()):
                return f"/static/audio/{filename}"
            else:
                print(f"⚠️ Edge-TTS crashed. Moving to Google TTS...")

        # --- STEP 2: Try Google TTS (Target Language) ---
        # This catches Punjabi/Odia/Assamese if Edge fails
        target_lang_code = gtts_code_map.get(language)
        
        if target_lang_code:
            print(f"🎤 Attempting Google TTS for {language} ({target_lang_code})...")
            try:
                tts = gTTS(text=clean_text, lang=target_lang_code, slow=False)
                tts.save(save_path)
                return f"/static/audio/{filename}"
            except Exception as e:
                print(f"❌ Google TTS failed for {language}: {e}")
                # If this fails, go to Step 3

        # --- STEP 3: Ultimate Fallback (Hindi) ---
        print("🚨 All methods failed. Fallback to Hindi.")
        try:
            tts = gTTS(text=clean_text, lang='hi', slow=False)
            tts.save(save_path)
            return f"/static/audio/{filename}"
        except:
            return None
         # © 2026 KisanMitra AI. All Rights Reserved.