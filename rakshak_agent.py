import fitz 
import io
import PIL.Image
from base_agent import BaseAgent

class KrishiRakshakAgent(BaseAgent):
    def __init__(self, project_id: str, location: str):
        super().__init__(project_id, location)

    def analyze_financial(self, file_path: str, language: str = "Hindi", location: str = "India", lat: str = None, lng: str = None):
        print(f"💰 Analyzing Financial Document: {file_path}")
        
        try:
            if file_path.lower().endswith('.pdf'):
                doc = fitz.open(file_path)
                page = doc.load_page(0)
                pix = page.get_pixmap()
                img_bytes = pix.tobytes("png")
                pil_image = PIL.Image.open(io.BytesIO(img_bytes))
            else:
                pil_image = PIL.Image.open(file_path)
            
            pil_image = pil_image.convert("RGB")
            pil_image.thumbnail((1024, 1024))
            
            prompt = f"""
System: You are an Expert Agricultural Economist, Insurance Actuary, and Government Scheme Advisor.
Language: {language}
Location: {location} (Lat: {lat}, Lng: {lng})

Instruction:
Read the attached agricultural diagnostic report (crop/cattle). Assess the financial risk, estimate yield loss, suggest applicable government insurance schemes (e.g., PMFBY, KCC), and estimate recovery costs.

Search the web specifically for "NABARD branches, Cooperative Banks, and Agriculture Loan Officers" near {location} (Lat: {lat}, Lng: {lng}).

CRITICAL LANGUAGE RULE: You MUST translate every dynamic string value generated for every key in the entire JSON object below (descriptions, summaries, eligibility criteria, action steps, names, roles, contact names, locations, video queries, and the audio script) into the exact requested user language. NO ENGLISH VALUES are permitted in the final dynamic JSON content, unless they are proper nouns of established English-named schemes that do not have regional language equivalents (like PMFBY). This is your #1 priority.

Enforce strict JSON output matching this exact structure:
{{
  "impact_summary": {{
    "risk_level": "High/Medium/Low",
    "estimated_loss_percent": "percentage string",
    "description": "Short description of impact"
  }},
  "stats": {{
    "financial_health_score": int (0-100),
    "vulnerability_index": int (0-100),
    "confidence": int (0-100)
  }},
  "insurance_schemes": [
    {{
      "name": "Scheme Name",
      "eligibility": "Eligibility criteria",
      "action_step": "How to apply"
    }}
  ],
  "recovery_cost": {{
    "estimated_cost": "Cost amount",
    "breakdown": "Cost breakdown details"
  }},
  "expert_contacts": [
     {{
       "name": "Name of Bank/Agent",
       "role": "Role",
       "contact": "Contact Info",
       "location": "Address/Location"
     }}
  ],
  "educational_videos": ["video topic 1", "video topic 2"],
  "audio_script": "A short reassuring audio script summarizing the financial risk and suggesting the immediate next step in {language}."
}}

CRITICAL JSON RULE: Return ONLY raw, valid JSON. Do not include markdown formatting, backticks, or extra conversational text. You MUST properly escape all double quotes (\") inside your translated string values to prevent JSON parsing errors.
"""
            raw_response = self._call_ai_model(prompt, pil_image, use_search=True)
            raw_text = raw_response.replace('```json', '').replace('```', '').strip()
            cleaned_json = self.clean_json_output(raw_text)
            if cleaned_json:
                return cleaned_json
            return self.get_fallback_data()
        except Exception as e:
             print(f"❌ Rakshak Analysis Error: {e}")
             return self.get_fallback_data()

    def get_fallback_data(self):
        return {
            "impact_summary": {
                "risk_level": "Unknown",
                "estimated_loss_percent": "N/A",
                "description": "Analysis failed to extract data."
            },
            "stats": {
                "financial_health_score": 0,
                "vulnerability_index": 50,
                "confidence": 0
            },
            "insurance_schemes": [],
            "recovery_cost": {
                "estimated_cost": "N/A",
                "breakdown": "N/A"
            },
            "expert_contacts": [],
            "educational_videos": [],
            "audio_script": "Analysis could not be completed at this time."
        }
