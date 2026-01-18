import json
import re
from pathlib import Path
import base64

from google import genai
from google.genai import types

from .config import config
from .models import WaterFootprintAnalysis, AnalysisError


SYSTEM_PROMPT = """You are an expert Environmental Scientist specialized in Virtual Water Footprints and Carbon Impact Analysis. Analyze products and provide comprehensive environmental impact estimates.

## Reference Data 

### TEXTILES (per item)
- Cotton T-shirt (250g): 2,700L water, 7kg CO2 (Green: 54%, Blue: 33%, Grey: 13%)
- Pair of Jeans (800g): 8,000L water, 33kg CO2 (Green: 45%, Blue: 40%, Grey: 15%)
- Leather Shoes: 8,000L water, 14kg CO2 (Green: 85%, Blue: 5%, Grey: 10%)
- Polyester Shirt: 500L water, 5.5kg CO2 (Green: 10%, Blue: 60%, Grey: 30%)
- Wool Sweater: 3,500L water, 27kg CO2 (Green: 78%, Blue: 12%, Grey: 10%)

### FOOD & BEVERAGES (per kg unless specified)
- Beef: 15,400L, 60kg CO2 (Green: 94%, Blue: 4%, Grey: 2%)
- Chicken: 4,300L, 6kg CO2 (Green: 82%, Blue: 7%, Grey: 11%)
- Pork: 6,000L, 12kg CO2 (Green: 82%, Blue: 8%, Grey: 10%)
- Eggs (per egg): 200L, 0.2kg CO2 (Green: 79%, Blue: 7%, Grey: 14%)
- Milk (per liter): 1,000L, 3kg CO2 (Green: 85%, Blue: 8%, Grey: 7%)
- Cheese: 5,000L, 24kg CO2 (Green: 85%, Blue: 8%, Grey: 7%)
- Rice: 2,500L, 4kg CO2 (Green: 48%, Blue: 44%, Grey: 8%)
- Coffee (per cup): 140L, 0.2kg CO2 (Green: 96%, Blue: 1%, Grey: 3%)
- Chocolate (100g): 1,700L, 0.6kg CO2 (Green: 98%, Blue: 1%, Grey: 1%)
- Apple: 820L, 0.5kg CO2 (Green: 68%, Blue: 16%, Grey: 16%)
- Banana: 790L, 0.7kg CO2 (Green: 84%, Blue: 12%, Grey: 4%)
- Avocado: 1,981L, 0.85kg CO2 (Green: 60%, Blue: 30%, Grey: 10%)
- Almonds: 16,000L, 5kg CO2 (Green: 40%, Blue: 50%, Grey: 10%)
- Wine (1 glass): 110L, 0.3kg CO2 (Green: 70%, Blue: 16%, Grey: 14%)
- Beer (1 pint): 150L, 0.3kg CO2 (Green: 85%, Blue: 5%, Grey: 10%)

### ELECTRONICS
- Smartphone: 13,000L, 85kg CO2 (Green: 10%, Blue: 70%, Grey: 20%)
- Laptop: 190,000L, 340kg CO2 (Green: 8%, Blue: 72%, Grey: 20%)
- Desktop Computer: 280,000L, 530kg CO2 (Green: 8%, Blue: 72%, Grey: 20%)
- Television: 75,000L, 370kg CO2 (Green: 5%, Blue: 75%, Grey: 20%)
- Tablet: 25,000L, 130kg CO2 (Green: 8%, Blue: 72%, Grey: 20%)

### PAPER
- A4 Paper (per sheet): 10 liters (Green: 60%, Blue: 25%, Grey: 15%)
- Book (300 pages): 3,000 liters (Green: 60%, Blue: 25%, Grey: 15%)

### VEHICLES
- Car (average): 400,000 liters (Green: 5%, Blue: 80%, Grey: 15%)
- Bicycle: 5,000 liters (Green: 20%, Blue: 60%, Grey: 20%)

## Water Types
- Green Water: Rainwater consumed by plants
- Blue Water: Surface/groundwater used in production
- Grey Water: Freshwater needed to dilute pollutants

## Instructions
1. Identify the product and estimate its water + carbon footprint
2. Calculate Green/Blue/Grey breakdown using reference data
3. Assess regional water stress impact (high stress regions amplify impact)
4. Suggest sustainable alternatives with real behavioral change potential
5. Provide actionable personal steps and collective impact potential

CRITICAL: Return ONLY a single valid JSON object. No markdown, no code blocks, no extra text.
Start with { and end with }. Ensure all fields are complete and properly formatted.

JSON Format:

{
    "product_name": "Product name",
    "product_category": "Textiles/Food/Electronics/Agriculture/Paper/Transport/Other",
    "total_liters": 0000,
    "carbon_kg": 00.0,
    "breakdown": {
        "green_water_pct": 00.0,
        "blue_water_pct": 00.0,
        "grey_water_pct": 00.0
    },
    "sustainable_swap": {
        "product_name": "Alternative",
        "water_liters": 0000,
        "carbon_kg": 00.0,
        "savings_liters": 0000,
        "savings_percentage": 00.0,
        "reasoning": "Why this is better"
    },
    "regional_impact": {
        "high_stress_regions": ["Region1", "Region2"],
        "scarcity_multiplier": 1.0,
        "context": "How this affects water-scarce areas"
    },
    "actionable_steps": [
        "Specific action user can take",
        "Another concrete step"
    ],
    "collective_impact": "If 1000 people switched, save X liters + Y kg CO2/year",
    "confidence_score": 0.00,
    "data_source": "WFN 2024 + IPCC Carbon Database",
    "fun_fact": "Compelling environmental fact"
}

If image is unclear:
{
    "error": true,
    "message": "Issue description",
    "suggestion": "How to improve"
}
"""


class WaterFootprintAnalyzer:
    def __init__(self, api_key=None):
        self.api_key = api_key or config.GEMINI_API_KEY
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is required. Set it in your .env file.")
        self.client = genai.Client(api_key=self.api_key)
        self.model_name = config.GEMINI_MODEL
    
    def _extract_json(self, text):
        text = text.strip()
        
        json_patterns = [
            r'```json\s*(\{.*?\})\s*```',
            r'```\s*(\{.*?\})\s*```',
            r'(\{.*\})',
        ]
        
        for pattern in json_patterns:
            match = re.search(pattern, text, re.DOTALL)
            if match:
                json_str = match.group(1).strip()
                try:
                    return json.loads(json_str)
                except json.JSONDecodeError:
                    continue
        
        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(
                f"Failed to parse JSON from response. Raw text: {text[:500]}",
                text, e.pos
            )
    
    def analyze_image(self, image_data, mime_type="image/jpeg"):
        try:
            img_b64 = base64.b64encode(image_data).decode('utf-8')
            
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[
                    types.Content(
                        role="user",
                        parts=[
                            types.Part(text=SYSTEM_PROMPT),
                            types.Part(text="\n\nAnalyze this product image:"),
                            types.Part(
                                inline_data=types.Blob(
                                    mime_type=mime_type,
                                    data=img_b64
                                )
                            )
                        ]
                    )
                ],
                config=types.GenerateContentConfig(
                    temperature=0.3,
                    top_p=0.8,
                    top_k=40,
                    max_output_tokens=2048,
                )
            )
            
            if not response.text:
                return AnalysisError(
                    error_type="empty_response",
                    message="Empty response from AI",
                    user_friendly_message="Couldn't analyze the image. Try a clearer photo with better lighting.",
                    retry_suggested=True
                )
            
            result = self._extract_json(response.text)
            
            if result.get("error"):
                return AnalysisError(
                    error_type="analysis_failed",
                    message=result.get("message", "Unknown error"),
                    user_friendly_message=result.get("suggestion", "Try with a clearer image."),
                    retry_suggested=True
                )
            
            return WaterFootprintAnalysis(**result)
            
        except json.JSONDecodeError as e:
            error_details = f"JSON error at position {e.pos}: {str(e)}"
            response_preview = response.text[:300] if 'response' in locals() and hasattr(response, 'text') else 'No response'
            
            return AnalysisError(
                error_type="parse_error",
                message=f"{error_details} | Response preview: {response_preview}",
                user_friendly_message="AI response format error. Retrying might help.",
                retry_suggested=True
            )
        except Exception as e:
            error_msg = str(e)
            error_type_name = type(e).__name__
            
            # Detailed error classification
            if "API_KEY" in error_msg.upper() or "401" in error_msg or "unauthorized" in error_msg.lower():
                friendly = "🔑 Invalid API key. Check your GEMINI_API_KEY in .env file"
                error_type = "auth_error"
            elif "quota" in error_msg.lower() or "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
                friendly = "🚦 API rate limit exceeded. Wait a minute and try again."
                error_type = "rate_limit"
            elif "404" in error_msg or "not found" in error_msg.lower():
                friendly = f"❌ Model '{self.model_name}' not available. Try gemini-2.5-flash"
                error_type = "model_not_found"
            elif "timeout" in error_msg.lower():
                friendly = "⏱️ Request timed out. Try again with smaller image."
                error_type = "timeout"
            elif "network" in error_msg.lower() or "connection" in error_msg.lower():
                friendly = "🌐 Network error. Check your internet connection."
                error_type = "network_error"
            else:
                friendly = f"⚠️ API Error: {error_msg[:200]}"
                error_type = "api_error"
            
            return AnalysisError(
                error_type=error_type,
                message=f"{error_type_name}: {error_msg}",
                user_friendly_message=friendly,
                retry_suggested=True
            )
    
    def analyze_from_file(self, file_path):
        path = Path(file_path)
        mime_types = {'.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.png': 'image/png', '.webp': 'image/webp'}
        mime_type = mime_types.get(path.suffix.lower(), 'image/jpeg')
        
        with open(path, 'rb') as f:
            return self.analyze_image(f.read(), mime_type)


_analyzer = None

def get_analyzer():
    global _analyzer
    if _analyzer is None:
        _analyzer = WaterFootprintAnalyzer()
    return _analyzer
