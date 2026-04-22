import io
import fitz  # PyMuPDF
from PIL import Image
from base_agent import BaseAgent
import json

class DhartiChakraAgent(BaseAgent):
    def get_fallback_data(self, error_msg):
        return {
            "weather_alerts": {"condition": "Unknown", "rain_probability": "0%", "alerts": error_msg},
            "soil_profile": {"soil_type": "Unknown", "characteristics": "Could not analyze."},
            "irrigation_planner": {"recommendation": "Hold", "schedule": "Check again later."},
            "crop_suitability": [{"crop_name": "Unknown", "reason": "Data unavailable"}],
            "agri_news": ["Unable to fetch news.", "Please try again later.", "System error."],
            "expert_contacts": [],
            "audio_script": "An error occurred while analyzing the weather and geological data."
        }

    def analyze_weather(self, file_path, language="Hindi", location="India", lat=None, lng=None):
        try:
            # SILENT CONVERTER & COMPRESSOR
            if file_path.lower().endswith('.pdf'):
                doc = fitz.open(file_path)
                page = doc.load_page(0)
                pix = page.get_pixmap()
                image_bytes = pix.tobytes("png")
                image = Image.open(io.BytesIO(image_bytes))
                doc.close()
            else:
                image = Image.open(file_path)

            image = image.convert("RGB")
            image.thumbnail((1024, 1024))

            geo_info = f"Location: {location} (Coordinates: {lat}, {lng})" if lat and lng else f"Location: {location}"

            master_prompt = f"""
            You are an Expert Meteorologist, Geologist, and Agronomist.

            Language: {language}
            {geo_info}

            Analyze the attached image (sky/soil/field). Using the exact GPS coordinates, use Google Search to fetch LIVE weather data, active IMD (Indian Meteorological Department) alerts, and regional soil health data.

            CRITICAL: Translate EVERY dynamic string value into the requested user language. Return ONLY raw, valid JSON. DO NOT use markdown formatting (```json). You MUST properly escape all double quotes inside strings.
            CRITICAL: Under `crop_suitability`, you MUST suggest highly specific crop varieties (e.g., 'Tomato (Pusa Ruby)', 'Okra (Bhindi)') based on the exact season and location. DO NOT use generic terms like 'Vegetables' or 'Grains'.

            JSON Structure:
            {{
                "weather_alerts": {{
                    "condition": "Current weather condition",
                    "rain_probability": "Percentage (e.g. 80%)",
                    "alerts": "Active IMD alerts or warnings"
                }},
                "soil_profile": {{
                    "soil_type": "Identified soil type",
                    "characteristics": "Detailed characteristics of the soil"
                }},
                "irrigation_planner": {{
                    "recommendation": "Specific irrigation recommendation",
                    "schedule": "Suggested schedule"
                }},
                "crop_suitability": [
                    {{
                        "crop_name": "Suitable crop 1",
                        "reason": "Why it is suitable"
                    }},
                    {{
                        "crop_name": "Suitable crop 2",
                        "reason": "Why it is suitable"
                    }}
                ],
                "agri_news": [
                    "Live news headline 1",
                    "Live news headline 2",
                    "Live news headline 3"
                ],
                "expert_contacts": [
                    {{
                        "name": "Expert Name/Office",
                        "role": "Role",
                        "contact": "Contact info",
                        "location": "Location"
                    }}
                ],
                "audio_script": "A short conversational summary of weather and soil advice."
            }}
            """

            # --- ATTEMPT 1: SEARCH MODE ---
            print("🔍 Attempting Dharti Analysis WITH Google Search...")
            try:
                search_instruction = master_prompt + " \n\nIMPORTANT: Use Google Search for real-time IMD weather, news, and geological data."
                raw_text = self._call_ai_model(search_instruction, image, use_search=True)
                
                # PARSER ARMOR
                raw_text = raw_text.replace('```json', '').replace('```', '').strip()
                data = self.clean_json_output(raw_text)
                if data and "weather_alerts" in data:
                    print("✅ Search Analysis Successful.")
                    return data
                else:
                    print("⚠️ Search output format invalid. Switching to Fallback...")
            except Exception as e:
                print(f"⚠️ Search failed ({e}). Switching to Fallback...")

            # --- ATTEMPT 2: FALLBACK MODE ---
            print("🔄 Retrying WITHOUT Search (Standard Analysis)...")
            fallback_instruction = master_prompt + " \n\nUse your internal expert knowledge base."
            raw_text = self._call_ai_model(fallback_instruction, image, use_search=False)
            
            raw_text = raw_text.replace('```json', '').replace('```', '').strip()
            data = self.clean_json_output(raw_text)
            if data and "weather_alerts" in data:
                return data
            
            return self.get_fallback_data("Both Search and Standard analysis failed to generate valid JSON.")

        except Exception as e:
            print(f"❌ Critical Error in Dharti Agent: {e}")
            return self.get_fallback_data(str(e))

    def generate_farm_plan(self, existing_data, land_area, land_unit, language="Hindi"):
        try:
            master_prompt = f"""
            You are a Master Agronomist. Read the following soil & weather report: {existing_data}. The farmer has {land_area} {land_unit} of land. Generate a highly actionable Kheti Ayojan (Farming Plan).

            CRITICAL: Translate EVERY dynamic string value into the requested user language ({language}). Return ONLY raw, valid JSON. DO NOT use markdown formatting (```json). You MUST properly escape all double quotes inside strings.

            JSON Structure:
            {{
                "seed_requirements": "Detailed amounts of seeds/fertilizer needed",
                "timeline": [
                    {{"step_name": "Step 1", "action": "Action description"}},
                    {{"step_name": "Step 2", "action": "Action description"}}
                ],
                "estimated_yield": "Predicted harvest output",
                "recommended_products": [
                    {{"name": "Product Name", "type": "Organic"}},
                    {{"name": "Product Name", "type": "Chemical"}}
                ],
                "setup_videos": [
                    "YouTube search query 1",
                    "YouTube search query 2",
                    "YouTube search query 3"
                ],
                "audio_script": "A 2-sentence vocal summary of the farming plan."
            }}
            """
            
            # The type must be strictly "Organic" or "Chemical" in English if the backend relies on it, but the prompt says just output type.
            # "type" [must be "Organic" or "Chemical"]

            print("🚜 Generating Farming Plan...")
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=master_prompt
            )
            raw_text = response.text if response else "{}"
            
            # PARSER ARMOR
            raw_text = raw_text.replace('```json', '').replace('```', '').strip()
            data = self.clean_json_output(raw_text)
            
            if data and "seed_requirements" in data:
                audio_path = None
                if "audio_script" in data and data["audio_script"]:
                    audio_path = self.generate_audio(data["audio_script"], language)
                data["audio_path"] = audio_path
                return data
            
            return {"error": "Failed to generate valid farm plan JSON."}
            
        except Exception as e:
            print(f"❌ Critical Error in Farming Plan: {e}")
            return {"error": str(e)}
