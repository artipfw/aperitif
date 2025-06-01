import os
import base64
from typing import Dict, Any, Optional
from openai import OpenAI

class VisionAgent:
    """Agent for analyzing San Francisco neighborhood maps"""
    
    def __init__(self, use_openai: bool = False):
        """
        Initialize the vision agent
        
        Args:
            use_openai: If True, use OpenAI's GPT-4 Vision. If False, use Phi-4
        """
        self.use_openai = use_openai
        
        if use_openai:
            # Use OpenAI's GPT-4 Vision
            api_key = os.environ.get("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY environment variable is required for OpenAI mode")
            
            self.client = OpenAI(api_key=api_key)
            self.model_name = "gpt-4o-mini"  # or "gpt-4-vision-preview" for better results
            print(f"Using OpenAI model: {self.model_name}")
        else:
            # Use Phi-4 endpoint
            self.client = OpenAI(
                api_key=os.environ.get("OPENAI_API_KEY", "fake"),
                base_url="https://phi-4-multimodal-instruct-guillaume-derouville-7ea5e77d.koyeb.app/v1",
            )
            self.model_name = "microsoft/Phi-4-multimodal-instruct"
            print(f"Using Phi-4 model: {self.model_name}")
        
        # San Francisco neighborhood types
        self.neighborhood_types = {
            "Offices": {"color": "blue", "description": "Business district, corporate area"},
            "Rich": {"color": "green", "description": "Wealthy residential area"},
            "Hip": {"color": "yellow", "description": "Trendy, artistic neighborhoods"},
            "Tourist": {"color": "red", "description": "Tourist hotspots, attractions"},
            "Uni": {"color": "dark blue", "description": "University area, student housing"},
            "Normies": {"color": "gray", "description": "Regular residential neighborhoods"}
        }
    
    def analyze_with_reference(self, legend_map_path: str, pin_map_path: str) -> Dict[str, Any]:
        """
        Analyze by comparing a legend/reference map with a pin map
        
        Args:
            legend_map_path: Path to map with colored zones and legend
            pin_map_path: Path to map with pin location
            
        Returns:
            Dictionary with neighborhood analysis
        """
        try:
            # Load and encode both images
            with open(legend_map_path, 'rb') as f:
                legend_b64 = base64.b64encode(f.read()).decode()
            
            with open(pin_map_path, 'rb') as f:
                pin_b64 = base64.b64encode(f.read()).decode()
            
            # Create a more specific prompt for two-image comparison
            prompt = """I'm showing you two images of San Francisco:

IMAGE 1 (Legend/Reference): A colored neighborhood map with zones and a legend at the bottom:
- Offices (blue) - Business districts
- Rich (green) - Wealthy residential areas  
- Hip (yellow) - Trendy, artistic neighborhoods
- Tourist (red) - Tourist areas
- Uni (dark blue) - University/student areas
- Normies (gray) - Regular residential neighborhoods

IMAGE 2 (Pin Map): A regular map with a red Google Maps pin marker.

IMPORTANT: These two images may have different zoom levels, scales, and orientations. You need to use landmark-based geographic reasoning to match locations between them.

Your task:
1. In IMAGE 2: Identify the pin's location using major landmarks, neighborhood names, and street patterns
2. In IMAGE 1: Use those same landmarks and geographic features to locate the corresponding area
3. In IMAGE 1: Carefully observe what COLOR zone that geographic area falls within
4. Match the observed color to the legend categories

CRITICAL NOTES:
- The pin is just a red location marker - ignore its color
- Focus on geographic landmarks like "Painted Ladies", "Japantown", major streets, parks
- The two maps may have different scales - use relative positioning to landmarks
- Look at the actual background color of the zone in IMAGE 1, not the pin color

Step-by-step process:
1. Identify specific landmarks near the pin in IMAGE 2
2. Find those same landmarks in IMAGE 1 (accounting for different scales)
3. Look at the general area around that location in IMAGE 1 (approximately 4-6 city blocks around the pin location)
4. Determine the PREDOMINANT color in that surrounding area
5. Match that predominant color to the legend

AREA ANALYSIS: Instead of looking at the exact pin point, examine the predominant color in the surrounding 4-6 blocks around the identified location. This accounts for mapping precision and scale differences.

Please respond with:
- Pin location: [specific landmarks and neighborhood where pin is placed]
- Surrounding area analysis: [describe the colors you see in the 4-6 blocks around that location]
- Predominant zone color: [the most common color in that area]
- Neighborhood type: [category from legend matching the predominant color]
- Reasoning: [how you matched the location and determined the predominant color]
- Confidence: [high/medium/low]"""

            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at comparing maps and identifying locations across different map views. Be very precise about matching locations between the two images."
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{legend_b64}"
                                }
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{pin_b64}"
                                }
                            }
                        ]
                    }
                ],
                temperature=0.1,
                max_tokens=400
            )
            
            # Parse the response
            analysis = response.choices[0].message.content
            
            # Extract neighborhood type from response
            neighborhood_type = None
            for ntype in self.neighborhood_types.keys():
                if ntype.lower() in analysis.lower():
                    neighborhood_type = ntype
                    break
            
            return {
                "success": True,
                "model_used": self.model_name,
                "raw_analysis": analysis,
                "neighborhood_type": neighborhood_type,
                "neighborhood_info": self.neighborhood_types.get(neighborhood_type, {}) if neighborhood_type else None,
                "error": None,
                "method": "two-image comparison"
            }
            
        except Exception as e:
            return {
                "success": False,
                "model_used": self.model_name,
                "raw_analysis": None,
                "neighborhood_type": None,
                "neighborhood_info": None,
                "error": str(e),
                "method": "two-image comparison"
            }

