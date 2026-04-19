from PIL import Image
from base_agent import BaseAgent

class KisanShayakAgent(BaseAgent):
    def get_fallback_data(self, error_msg):
        return {
            "diagnoses": [{
                "disease_name": f"⚠️ Analysis error",
                "description": error_msg,
                "confidence": "0",
                "organic_remedy": "Please try again.",
                "chemical_remedy": "Please try again."
            }],
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

    def analyze_crop(self, image_path, user_query=None, language="Hindi", location="India", lat=None, lng=None):
        try:
            pil_image = Image.open(image_path)
            if not user_query: user_query = "What is wrong with my plant?"
            
            geo_info = f"Location: {location} (Coordinates: {lat}, {lng})" if lat and lng else f"Location: {location}"

            # --- MASTER PROMPT ---
            master_prompt = f"""
            You are 'KisanShayak', an expert Forensic Plant Pathologist, Agricultural Market Analyst, and experienced Agronomist who provides best relevant results.
            
            User Query: "{user_query}"
            Language: {language}
            {geo_info}
            
            TASK:
            1. **Forensic Diagnosis:** Identify crop, disease, pathogen lifecycle, and specific visual symptoms accurately.
            2. **Cures:** Provide specific Organic (Priority) and Chemical remedies.
            3. **Local Intelligence:** Provide realistic details for KVK/Agri Officers, Plant Pathologists, Major Agrochemical Companies near the provided location.
            4. **Market Analysis:** Properly compare Costs vs Risk.
            
            CRITICAL JSON RULES (Do NOT remove these or the app will crash):
            - Return ONLY a valid JSON object. No intro text.
            - **Enclose ALL KEYS and ALL VALUES in double quotes.**
            - Translate ALL strings to {language}.
            
            JSON Structure:
            {{
                "diagnoses": [
                    {{
                        "disease_name": "Name of the disease",
                        "description": "Detailed description {language}.",
                        "confidence": "Integer 0-100 (as string)",
                        "organic_remedy": "Organic cures {language}",
                        "chemical_remedy": "Chemical cures {language}"
                    }}
                ],
                "audio_script": "Best possible proper conversational summary. Refer user to expert sections and prefer organic remedies (Max 3 sentences) {language}.",
                "stats": {{ 
                    "health_score": "Integer 0-100 (as string)", 
                    "infection_severity": "Low/Medium/High (Translated string)", 
                    "confidence": "Integer 0-100 (as string)" 
                }},
                "remedies_video_queries": ["Query 1", "Query 2", "Query 3"],
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
            
            Note: If the image is confusing or points to multiple diseases, provide up to 3 possibilities in the diagnoses array. If highly confident, provide only 1.
            """

            # --- ATTEMPT 1: SEARCH MODE ---
            print("🔍 Attempting Analysis WITH Google Search...")
            try:
                search_instruction = master_prompt + " \n\nIMPORTANT: Use Google Search for accurate and relevant real-time data. Do NOT include citation markers like [1] in the JSON output."
                raw_text = self._call_ai_model(search_instruction, pil_image, use_search=True)
                
                data = self.clean_json_output(raw_text)
                if data and "diagnoses" in data:
                    print("✅ Search Analysis Successful.")
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
            if data and "diagnoses" in data:
                return data
            
            return self.get_fallback_data("Both Search and Standard analysis failed to generate valid JSON.")

        except Exception as e:
            print(f"❌ Critical Error: {e}")
            return self.get_fallback_data(str(e))

# © 2026 Paaras Shemrudkar & Prachi Sharma (Owners of KisanMitra AI/Krishi Shayak AI). All rights reserved.