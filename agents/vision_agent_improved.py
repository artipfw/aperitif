import os
import base64
from typing import Dict, Any, Optional, Tuple
from openai import OpenAI
from PIL import Image, ImageEnhance, ImageOps
import io

class ImprovedVisionAgent:
    """Improved agent with image preprocessing for better Phi-4 compatibility"""
    
    def __init__(self):
        # Use the Phi-4 endpoint with OpenAI client
        self.client = OpenAI(
            api_key=os.environ.get("OPENAI_API_KEY", "fake"),
            base_url="https://phi-4-multimodal-instruct-guillaume-derouville-7ea5e77d.koyeb.app/v1",
        )
        
        # San Francisco neighborhood types
        self.neighborhood_types = {
            "Offices": {"color": "blue", "description": "Business district, corporate area"},
            "Rich": {"color": "green", "description": "Wealthy residential area"},
            "Hip": {"color": "yellow", "description": "Trendy, artistic neighborhoods"},
            "Tourist": {"color": "red", "description": "Tourist hotspots, attractions"},
            "Uni": {"color": "dark blue", "description": "University area, student housing"},
            "Normies": {"color": "gray", "description": "Regular residential neighborhoods"}
        }
    
    def preprocess_image(self, image_path: str, save_debug: bool = True) -> Tuple[str, Dict[str, Any]]:
        """
        Preprocess image for better Phi-4 compatibility
        
        Returns:
            Tuple of (base64_encoded_image, metadata)
        """
        metadata = {}
        
        try:
            with Image.open(image_path) as img:
                original_size = img.size
                metadata['original_size'] = original_size
                
                # Convert RGBA to RGB if needed
                if img.mode == 'RGBA':
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[3])
                    img = background
                
                # 1. Crop to focus on the map area (remove UI elements)
                # Assuming the map is in the center, crop out browser chrome
                width, height = img.size
                crop_top = int(height * 0.1)  # Remove top 10%
                crop_bottom = int(height * 0.9)  # Remove bottom 10%
                crop_left = int(width * 0.05)  # Remove left 5%
                crop_right = int(width * 0.95)  # Remove right 5%
                
                img_cropped = img.crop((crop_left, crop_top, crop_right, crop_bottom))
                
                # 2. Resize to optimal size for Phi-4
                max_dimension = 800
                img_cropped.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)
                
                # 3. Enhance contrast and sharpness
                enhancer = ImageEnhance.Contrast(img_cropped)
                img_enhanced = enhancer.enhance(1.5)
                
                enhancer = ImageEnhance.Sharpness(img_enhanced)
                img_enhanced = enhancer.enhance(1.5)
                
                # 4. Save debug versions if requested
                if save_debug:
                    img_cropped.save('debug_cropped.png')
                    img_enhanced.save('debug_enhanced.png')
                    print(f"Debug images saved: debug_cropped.png, debug_enhanced.png")
                
                # Convert to base64
                buffer = io.BytesIO()
                img_enhanced.save(buffer, format='PNG', optimize=True, quality=85)
                buffer.seek(0)
                
                metadata['processed_size'] = img_enhanced.size
                metadata['file_size_kb'] = buffer.tell() / 1024
                
                return base64.b64encode(buffer.read()).decode(), metadata
                
        except Exception as e:
            print(f"Error preprocessing image: {e}")
            # Fallback to original
            with open(image_path, 'rb') as f:
                return base64.b64encode(f.read()).decode(), metadata
    
    def analyze_step_by_step(self, map_path: str) -> Dict[str, Any]:
        """
        Analyze map using step-by-step approach for better results
        """
        try:
            # Preprocess image
            print("Preprocessing image...")
            image_b64, metadata = self.preprocess_image(map_path)
            print(f"Image processed: {metadata}")
            
            # Step 1: Verify it's a map
            response1 = self.client.chat.completions.create(
                model="microsoft/Phi-4-multimodal-instruct",
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Is this a map? Answer with one word: yes or no"},
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_b64}"}}
                    ]
                }],
                temperature=0.1,
                max_tokens=10
            )
            is_map = "yes" in response1.choices[0].message.content.lower()
            
            if not is_map:
                return {
                    "success": False,
                    "error": "Image does not appear to be a map"
                }
            
            # Step 2: Identify dominant colors
            response2 = self.client.chat.completions.create(
                model="microsoft/Phi-4-multimodal-instruct",
                messages=[{
                    "role": "user", 
                    "content": [
                        {"type": "text", "text": "What are the main colors visible in this map? List only color names, separated by commas."},
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_b64}"}}
                    ]
                }],
                temperature=0.1,
                max_tokens=50
            )
            colors_found = response2.choices[0].message.content
            
            # Step 3: Look for pin/marker
            response3 = self.client.chat.completions.create(
                model="microsoft/Phi-4-multimodal-instruct",
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Is there a pin, marker, or pointer visible on this map? Answer: yes or no"},
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_b64}"}}
                    ]
                }],
                temperature=0.1,
                max_tokens=10
            )
            has_pin = "yes" in response3.choices[0].message.content.lower()
            
            # Step 4: Final analysis with context
            final_prompt = f"""This is a neighborhood map. The colors represent:
- Blue = Offices
- Green = Rich  
- Yellow = Hip
- Red = Tourist
- Dark Blue = Uni
- Gray = Normies

Colors found in image: {colors_found}
Pin detected: {has_pin}

Based on this information, what type of neighborhood is marked or most prominent?
Answer with just the neighborhood type name."""

            response_final = self.client.chat.completions.create(
                model="microsoft/Phi-4-multimodal-instruct",
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": final_prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_b64}"}}
                    ]
                }],
                temperature=0.1,
                max_tokens=50
            )
            
            final_analysis = response_final.choices[0].message.content
            
            # Extract neighborhood type
            neighborhood_type = None
            for ntype in self.neighborhood_types.keys():
                if ntype.lower() in final_analysis.lower():
                    neighborhood_type = ntype
                    break
            
            return {
                "success": True,
                "raw_analysis": f"Step 1 (is map): {is_map}\nStep 2 (colors): {colors_found}\nStep 3 (has pin): {has_pin}\nFinal: {final_analysis}",
                "neighborhood_type": neighborhood_type,
                "neighborhood_info": self.neighborhood_types.get(neighborhood_type, {}) if neighborhood_type else None,
                "metadata": metadata,
                "error": None
            }
            
        except Exception as e:
            return {
                "success": False,
                "raw_analysis": None,
                "neighborhood_type": None,
                "neighborhood_info": None,
                "error": str(e)
            }
    
    def analyze(self, map_path: str) -> Dict[str, Any]:
        """Main entry point - uses step-by-step approach"""
        return self.analyze_step_by_step(map_path)

# Keep the original VisionAgent for comparison
from agents.vision_agent import VisionAgent