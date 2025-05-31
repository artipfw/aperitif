import os
import base64
from openai import OpenAI
from pathlib import Path

# Use the working Phi-4 endpoint
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY", "fake"),
    base_url="https://phi-4-multimodal-instruct-guillaume-derouville-7ea5e77d.koyeb.app/v1",
)

def test_vision_with_base64_images():
    """Test vision capability with base64 encoded images"""
    
    # Create test images directory
    Path("test_images").mkdir(exist_ok=True)
    
    # For testing, let's create a simple colored square using PIL
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        # Create region map with colored areas and legend
        region_map = Image.new('RGB', (800, 600), 'white')
        draw = ImageDraw.Draw(region_map)
        
        # Draw colored regions
        colors = {
            'District A': '#FF0000',  # Red
            'District B': '#00FF00',  # Green
            'District C': '#0000FF',  # Blue
            'District D': '#FFFF00',  # Yellow
        }
        
        # Draw regions (simple rectangles)
        draw.rectangle([0, 0, 400, 300], fill='#FF0000')      # District A - Red
        draw.rectangle([400, 0, 800, 300], fill='#00FF00')    # District B - Green
        draw.rectangle([0, 300, 400, 600], fill='#0000FF')    # District C - Blue
        draw.rectangle([400, 300, 800, 600], fill='#FFFF00')  # District D - Yellow
        
        # Draw legend
        y_offset = 50
        for district, color in colors.items():
            draw.rectangle([650, y_offset, 680, y_offset + 20], fill=color)
            draw.text((690, y_offset), district, fill='black')
            y_offset += 30
        
        region_map.save('test_images/region_map.png')
        
        # Create pin map (same layout but with a pin)
        pin_map = region_map.copy()
        draw_pin = ImageDraw.Draw(pin_map)
        
        # Draw a pin at coordinates (200, 150) - should be in District A (red)
        pin_x, pin_y = 200, 150
        # Draw pin circle
        draw_pin.ellipse([pin_x-10, pin_y-10, pin_x+10, pin_y+10], fill='black')
        # Draw pin point
        draw_pin.polygon([(pin_x, pin_y+10), (pin_x-10, pin_y+20), (pin_x+10, pin_y+20)], fill='black')
        
        pin_map.save('test_images/pin_map.png')
        
        print("✅ Created test images successfully")
        
    except ImportError:
        print("❌ PIL not available. Please place test images manually in test_images/")
        return
    
    # Load and encode images
    with open('test_images/region_map.png', 'rb') as f:
        region_map_b64 = base64.b64encode(f.read()).decode()
    
    with open('test_images/pin_map.png', 'rb') as f:
        pin_map_b64 = base64.b64encode(f.read()).decode()
    
    print("\nTesting Phi-4 multimodal with map images...")
    print("-" * 50)
    
    # Test multimodal request
    try:
        response = client.chat.completions.create(
            model="microsoft/Phi-4-multimodal-instruct",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert at analyzing maps and colors. Be precise and specific."
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "I have two images. The first shows a map divided into 4 colored districts (red, green, blue, yellow) with a legend. The second shows the same map with a black pin. What color district is the pin located in? Please identify: 1) The color name, 2) The district name from the legend, 3) The approximate RGB values of that color."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{region_map_b64}"
                            }
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{pin_map_b64}"
                            }
                        }
                    ]
                }
            ],
            temperature=0.1,
            max_tokens=300
        )
        
        print("✅ Response received!")
        print(f"\nAnalysis: {response.choices[0].message.content}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print(f"Error type: {type(e).__name__}")


def test_simple_vision():
    """Test with a simple vision request"""
    print("Testing basic vision capability...")
    
    try:
        response = client.chat.completions.create(
            model="microsoft/Phi-4-multimodal-instruct",
            messages=[
                {
                    "role": "user",
                    "content": "Can you analyze images? If yes, what types of images can you process?"
                }
            ],
            max_tokens=100
        )
        
        print(f"Response: {response.choices[0].message.content}")
        
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    print("Phi-4 Multimodal Vision Test")
    print("=" * 50)
    
    # Test basic capability
    test_simple_vision()
    
    print("\n")
    
    # Test with actual images
    test_vision_with_base64_images()