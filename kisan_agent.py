import os
import uuid
from google import genai
from PIL import Image
from gtts import gTTS

class KisanMitraAgent:
    def __init__(self, project_id, location):
        if not project_id or not location:
            raise ValueError("GCP Project ID or Location is missing.")
        
        # --- VERTEX AI INITIALIZATION ---
        print(f"🔄 Connecting to Vertex AI (Project: {project_id}, Region: {location})...")
        try:
            self.client = genai.Client(
                vertexai=True, 
                project=project_id, 
                location=location
            )
            
            # --- MODEL SELECTION ---
            # Using the specific stable version for 2026
            self.model_name = "gemini-2.5-flash"
            print(f"✅ KisanMitra Agent initialized using: {self.model_name}")
            
        except Exception as e:
            print(f"❌ Failed to initialize Vertex AI Client: {e}")
            raise e

    def analyze_crop(self, image_path, user_query=None, language="Hindi"):
        """
        1. Reads the crop image.
        2. Considers the farmer's question.
        3. Returns a diagnosis + cure.
        """
        try:
            pil_image = Image.open(image_path)
            
            if not user_query:
                user_query = "What is wrong with my plant?"

            # The Expert Agronomist Prompt
            prompt = f"""
            You are 'KisanMitra', an expert Agronomist and Plant Pathologist.
            
            User's Query: "{user_query}"
            Language Requested: {language}
            
            TASK:
            1. Analyze the image. identify the crop and the disease/pest.
            2. If no disease is visible, say "The plant looks healthy."
            3. Suggest a CURE:
               - First: An Organic/Home remedy (low cost).
               - Second: A Safe Chemical remedy (with exact dosage).
            4. STRICTLY avoid harmful overdoses.
            
            OUTPUT FORMAT:
            Provide the response in simple {language}. 
            Keep it conversational and empathetic (e.g., "Namaste! Don't worry...").
            Do not use complex formatting (no markdown tables), as this will be spoken out loud.
            """

            # Call Vertex AI
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[prompt, pil_image]
            )
            
            return response.text if response else "Error: AI could not diagnose."

        except Exception as e:
            print(f"Analysis Error: {e}")
            return f"Error in analysis: {str(e)}"

    def generate_audio(self, text, language="Hindi"):
        """
        Converts the text diagnosis into an MP3 file using gTTS.
        """
        try:
            lang_codes = {'Hindi': 'hi', 'English': 'en', 'Marathi': 'mr', 'Tamil': 'ta'}
            code = lang_codes.get(language, 'hi')
            
            tts = gTTS(text=text, lang=code, slow=False)
            
            filename = f"response_{uuid.uuid4().hex[:8]}.mp3"
            save_path = os.path.join("static", "audio", filename)
            
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            
            tts.save(save_path)
            return f"/static/audio/{filename}"
        except Exception as e:
            print(f"Audio Error: {e}")
            return None