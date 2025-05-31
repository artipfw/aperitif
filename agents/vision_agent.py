import os
import base64
from typing import Dict, Any
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
    
    def analyze(self, map_path: str) -> Dict[str, Any]:
        """
        Analyze a San Francisco map image that has colored zones, legend, and a pin
        
        Args:
            map_path: Path to the map image with zones, legend, and pin
            
        Returns:
            Dictionary with neighborhood analysis
        """
        try:
            # Load and encode image
            with open(map_path, 'rb') as f:
                image_b64 = base64.b64encode(f.read()).decode()
            
            # Create the analysis prompt
            prompt = """This is a San Francisco neighborhood map with colored zones and a legend at the bottom showing:
- Offices (blue) - Business districts
- Rich (green) - Wealthy residential areas  
- Hip (yellow) - Trendy, artistic neighborhoods
- Tourist (red) - Tourist areas
- Uni (dark blue) - University/student areas
- Normies (gray) - Regular residential neighborhoods

I can see a pin/marker on this map. Please:
1. Identify where the pin is located
2. Determine which colored zone the pin falls within
3. Match that zone to the legend category

Please respond with:
- Neighborhood type: [exact category from legend - must be one of: Offices, Rich, Hip, Tourist, Uni, Normies]
- Color observed: [color name]
- Location description: [brief description of where the pin is]
- Confidence: [high/medium/low]"""

            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at reading maps and identifying neighborhood zones. Focus on the pin location and the colored zone it falls within. Be precise and specific."
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
                                    "url": f"data:image/png;base64,{image_b64}"
                                }
                            }
                        ]
                    }
                ],
                temperature=0.1,
                max_tokens=300
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
                "error": None
            }
            
        except Exception as e:
            return {
                "success": False,
                "model_used": self.model_name,
                "raw_analysis": None,
                "neighborhood_type": None,
                "neighborhood_info": None,
                "error": str(e)
            }

# For future multi-agent integration with agno
from agno.agent import Agent
from agno.models.openai import OpenAIChat

class AgnoVisionAgent(VisionAgent):
    """Extended version for agno multi-agent workflows"""
    
    def __init__(self, use_openai: bool = False):
        super().__init__(use_openai)
        
        if use_openai:
            # Initialize agno agent with OpenAI
            self.agno_model = OpenAIChat(
                id="gpt-4o-mini",
                api_key=os.environ.get("OPENAI_API_KEY")
            )
        else:
            # Initialize agno agent with Phi-4
            self.agno_model = OpenAIChat(
                api_key=os.environ.get("OPENAI_API_KEY", "fake"),
                base_url="https://phi-4-multimodal-instruct-guillaume-derouville-7ea5e77d.koyeb.app/v1",
                id="microsoft/Phi-4-multimodal-instruct"
            )
        
        self.agno_agent = Agent(
            model=self.agno_model,
            instructions="""You are an expert at analyzing San Francisco neighborhood maps.
            Focus on identifying pin locations and matching them to neighborhood types.""",
            markdown=True
        )