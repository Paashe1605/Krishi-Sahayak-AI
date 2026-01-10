import os
import uuid
import time
from google import genai
from PIL import Image
from gtts import gTTS

class KisanMitraAgent:
    def __init__(self, api_key):
        if not api_key:
            raise ValueError("API Key is missing.")
        
        # Initialize Gemini Client
        self.client = genai.Client(api_key=api_key)
        
        # --- AUTO-DISCOVERY MAGIC (From Miyavkify) ---
        print("🔄 Asking Google for available models...")
        self.model_name = self._find_best_model()
        print(f"✅ KisanMitra Agent initialized using: {self.model_name}")

    def _find_best_model(self):
        """
        Asks Google which models are available and picks the best 'Flash' model.
        """
        try:
            # 1. Ask Google for list of models
            available_models = self.client.models.list()
            model_names = [m.name for m in available_models]
            
            # 2. Look for 'Flash' (Fastest for images)
            for name in model_names:
                if "flash" in name.lower() and "exp" not in name.lower() and "8b" in name.lower():
                    return name  # Best: Flash 8b (Super fast)
            
            for name in model_names:
                if "flash" in name.lower() and "exp" not in name.lower():
                    return name  # Good: Standard Flash
            
            # 3. Fallback to Pro if Flash is missing
            for name in model_names:
                if "pro" in name.lower() and "vision" not in name.lower():
                    return name
            
            # 4. Absolute Fallback
            return "gemini-1.5-flash"
            
        except Exception as e:
            print(f"⚠️ Model Discovery Failed: {e}. Using default.")
            return "gemini-1.5-flash"

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
            1. Analyze the image. identify the crop and the disease/pest.(Note have clean and highly relevant dataset/data source to identify the disease/pest)
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

            # Call Gemini using the Auto-Discovered Model
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[prompt, pil_image]
            )
            
            return response.text if response else "Error: AI could not diagnose."

        except Exception as e:
            return f"Error in analysis: {str(e)}"

    def generate_audio(self, text, language="Hindi"):
        """
        Converts the text diagnosis into an MP3 file.
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