#!/usr/bin/env python3
"""Diagnostic script to understand Phi-4's vision capabilities"""

import os
import base64
from openai import OpenAI
from PIL import Image
import io

def test_phi4_basic():
    """Test basic Phi-4 capabilities"""
    client = OpenAI(
        api_key="fake",
        base_url="https://phi-4-multimodal-instruct-guillaume-derouville-7ea5e77d.koyeb.app/v1",
    )
    
    print("Test 1: Basic text-only query")
    print("-" * 50)
    try:
        response = client.chat.completions.create(
            model="microsoft/Phi-4-multimodal-instruct",
            messages=[{"role": "user", "content": "What is 2+2?"}],
            temperature=0.1,
            max_tokens=50
        )
        print(f"✅ Response: {response.choices[0].message.content}")
    except Exception as e:
        print(f"❌ Error: {e}")

def analyze_image_properties(image_path):
    """Analyze image properties"""
    print(f"\nImage Analysis: {image_path}")
    print("-" * 50)
    
    try:
        with Image.open(image_path) as img:
            print(f"Format: {img.format}")
            print(f"Size: {img.size}")
            print(f"Mode: {img.mode}")
            
            # Check file size
            file_size = os.path.getsize(image_path)
            print(f"File size: {file_size / 1024:.1f} KB")
            
            # Try to reduce image size if too large
            if file_size > 500 * 1024:  # 500KB
                print("\n⚠️  Image is large, creating smaller version...")
                
                # Resize image
                max_size = (800, 800)
                img.thumbnail(max_size, Image.Resampling.LANCZOS)
                
                # Save to buffer
                buffer = io.BytesIO()
                img.save(buffer, format='PNG', optimize=True)
                buffer.seek(0)
                
                return base64.b64encode(buffer.read()).decode()
            else:
                with open(image_path, 'rb') as f:
                    return base64.b64encode(f.read()).decode()
                    
    except Exception as e:
        print(f"❌ Error analyzing image: {e}")
        return None

def test_simple_vision():
    """Test with a very simple prompt"""
    client = OpenAI(
        api_key="fake",
        base_url="https://phi-4-multimodal-instruct-guillaume-derouville-7ea5e77d.koyeb.app/v1",
    )
    
    print("\nTest 2: Simple vision test")
    print("-" * 50)
    
    # Load image
    image_b64 = analyze_image_properties("example_image.png")
    if not image_b64:
        return
    
    # Try different prompts
    prompts = [
        "What do you see in this image?",
        "Describe the colors you see.",
        "Is there a map in this image? Yes or no.",
        "What color is at the center of the image?",
    ]
    
    for prompt in prompts:
        print(f"\nPrompt: {prompt}")
        try:
            response = client.chat.completions.create(
                model="microsoft/Phi-4-multimodal-instruct",
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_b64}"}}
                    ]
                }],
                temperature=0.1,
                max_tokens=100
            )
            print(f"Response: {response.choices[0].message.content[:200]}")
        except Exception as e:
            print(f"Error: {e}")

def test_with_preprocessed_image():
    """Test with a preprocessed/simplified image"""
    print("\nTest 3: Creating simplified test image")
    print("-" * 50)
    
    try:
        # Create a simple test image with clear zones
        from PIL import Image, ImageDraw, ImageFont
        
        # Create image
        img = Image.new('RGB', (600, 400), 'white')
        draw = ImageDraw.Draw(img)
        
        # Draw colored zones
        colors = {
            'red': (255, 0, 0),
            'green': (0, 255, 0),
            'blue': (0, 0, 255),
            'yellow': (255, 255, 0)
        }
        
        # Draw quadrants
        draw.rectangle([0, 0, 300, 200], fill=colors['red'])
        draw.rectangle([300, 0, 600, 200], fill=colors['green'])
        draw.rectangle([0, 200, 300, 400], fill=colors['blue'])
        draw.rectangle([300, 200, 600, 400], fill=colors['yellow'])
        
        # Add a black pin in the red zone
        pin_x, pin_y = 150, 100
        draw.ellipse([pin_x-15, pin_y-15, pin_x+15, pin_y+15], fill='black')
        
        # Save
        img.save('test_simple_map.png')
        print("✅ Created test_simple_map.png")
        
        # Test with this image
        client = OpenAI(
            api_key="fake",
            base_url="https://phi-4-multimodal-instruct-guillaume-derouville-7ea5e77d.koyeb.app/v1",
        )
        
        with open('test_simple_map.png', 'rb') as f:
            simple_b64 = base64.b64encode(f.read()).decode()
        
        response = client.chat.completions.create(
            model="microsoft/Phi-4-multimodal-instruct",
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": "This image has 4 colored zones: red (top-left), green (top-right), blue (bottom-left), yellow (bottom-right). There is a black circle marking a location. Which colored zone is the black circle in?"},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{simple_b64}"}}
                ]
            }],
            temperature=0.1,
            max_tokens=100
        )
        print(f"\nSimple map response: {response.choices[0].message.content}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def test_map_extraction():
    """Try to extract just the map portion"""
    print("\nTest 4: Map extraction approach")
    print("-" * 50)
    
    client = OpenAI(
        api_key="fake", 
        base_url="https://phi-4-multimodal-instruct-guillaume-derouville-7ea5e77d.koyeb.app/v1",
    )
    
    # Load image
    with open("example_image.png", 'rb') as f:
        image_b64 = base64.b64encode(f.read()).decode()
    
    # Try step-by-step approach
    steps = [
        "Is this a map of San Francisco? Answer yes or no only.",
        "Can you see a legend at the bottom of the image? Answer yes or no only.",
        "List the colors you can see in the legend. Just list colors, nothing else.",
        "Is there a pin or marker on the map? Answer yes or no only.",
    ]
    
    for step in steps:
        print(f"\nStep: {step}")
        try:
            response = client.chat.completions.create(
                model="microsoft/Phi-4-multimodal-instruct",
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": step},
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_b64}"}}
                    ]
                }],
                temperature=0.1,
                max_tokens=50
            )
            print(f"Response: {response.choices[0].message.content}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    print("Phi-4 Vision Diagnostics")
    print("=" * 50)
    
    test_phi4_basic()
    test_simple_vision()
    test_with_preprocessed_image()
    test_map_extraction()