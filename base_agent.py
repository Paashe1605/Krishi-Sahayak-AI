import os
import json
import re
import uuid
import asyncio
from typing import Optional
from google import genai
from google.genai import types
from google.cloud import texttospeech
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

class BaseAgent:
    def __init__(self, project_id: str, location: str):
        if not project_id or not location:
            raise ValueError("GCP Project ID or Location is missing.")
        
        print(f"🔄 Connecting to Vertex AI (Project: {project_id}, Region: {location})...")
        try:
            self.client = genai.Client(vertexai=True, project=project_id, location=location)
            self.model_name = "gemini-2.5-flash"
            print(f"✅ BaseAgent initialized using: {self.model_name}")
        except Exception as e:
            print(f"❌ Failed to initialize Vertex AI Client: {e}")
            raise e

    def clean_text(self, text: str) -> str:
        """Cleans text for TTS and Display (removes markdown)."""
        if not text: return ""
        if isinstance(text, (dict, list)): return str(text)
        
        clean = re.sub(r'\*\*|__', '', text) 
        clean = re.sub(r'#+', '', clean)
        clean = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', clean) # Remove links
        clean = re.sub(r'^\*\s', '• ', clean, flags=re.MULTILINE) 
        return clean.strip()

    def extract_json_with_brace_counting(self, text: str) -> Optional[dict]:
        """Surgically extracts the first valid JSON object using brace counting."""
        try:
            start_index = text.find('{')
            if start_index == -1: return None
            
            count = 0
            for i in range(start_index, len(text)):
                if text[i] == '{': count += 1
                elif text[i] == '}':
                    count -= 1
                    if count == 0:
                        json_candidate = text[start_index:i+1]
                        return json.loads(json_candidate)
            return None
        except Exception:
            return None

    def clean_json_output(self, raw_text: str) -> Optional[dict]:
        """Sanitizer: Removes Search Citations and parses JSON."""
        if not raw_text: return None
        try:
            text = re.sub(r'\[\d+\]', '', raw_text)
            text = re.sub(r'【.*?】', '', text)
            
            extracted_data = self.extract_json_with_brace_counting(text)
            if extracted_data: return extracted_data

            text = re.sub(r'```json\s*', '', text)
            text = re.sub(r'```\s*', '', text)
            
            start = text.find('{')
            end = text.rfind('}') + 1
            if start != -1 and end != -1:
                json_str = text[start:end]
                json_str = re.sub(r',\s*}', '}', json_str)
                return json.loads(json_str)
            
            return json.loads(text)
        except Exception as e:
            print(f"⚠️ JSON Parse Error: {e}")
            return None

    def _call_ai_model(self, prompt: str, pil_image, use_search=False) -> str:
        config_args = {'temperature': 0.3}
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

    def generate_audio(self, text: str, language: str = "Hindi") -> Optional[str]:
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

            # ATTEMPT 1: EdgeTTS
            if language in edge_voice_map:
                try:
                    async def _save_edge():
                        communicate = edge_tts.Communicate(clean_text, edge_voice_map[language])
                        await communicate.save(save_path)
                    run_async_tts(_save_edge())
                    return f"/static/audio/{filename}"
                except Exception as e:
                    print(f"⚠️ EdgeTTS Failed ({e}), switching to Google TTS fallback...")

            # ATTEMPT 2: Google Cloud TTS Fallback
            lang_codes = {
                'Hindi': 'hi-IN', 'English': 'en-IN', 'Marathi': 'mr-IN', 
                'Tamil': 'ta-IN', 'Gujarati': 'gu-IN', 'Punjabi': 'pa-IN', 'Bengali': 'bn-IN'
            }
            lang_code = lang_codes.get(language, 'hi-IN')
            
            client = texttospeech.TextToSpeechClient()
            synthesis_input = texttospeech.SynthesisInput(text=clean_text)
            voice = texttospeech.VoiceSelectionParams(
                language_code=lang_code,
                ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
            )
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3
            )
            
            response = client.synthesize_speech(
                input=synthesis_input, voice=voice, audio_config=audio_config
            )
            
            with open(save_path, "wb") as out:
                out.write(response.audio_content)
                
            return f"/static/audio/{filename}"

        except Exception as e:
            print(f"Audio Error: {e}")
            return None
# © 2026 Paaras Shemrudkar & Prachi Sharma (Owners of KisanMitra AI/Krishi Shayak AI). All rights reserved.
