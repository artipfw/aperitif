#!/usr/bin/env python3
"""Test the VisionAgent for neighborhood analysis"""

import os
from agents.vision_agent import VisionAgent

def main():
    print("San Francisco Neighborhood Analysis Test")
    print("=" * 50)
    
    # Initialize the agent
    agent = VisionAgent()
    
    # Test with your example_image.png
    if os.path.exists("example_image.png"):
        print("\nAnalyzing example_image.png...")
        print("-" * 50)
        
        try:
            print("Making API call...")
            result = agent.analyze("example_image.png")
            print("API call completed")
        except Exception as e:
            print(f"Exception during API call: {e}")
            result = {"success": False, "error": str(e)}
        
        if result["success"]:
            print("✅ Analysis successful!")
            print(f"\nRaw Analysis:\n{result['raw_analysis']}")
            
            if result["neighborhood_type"]:
                print(f"\n🏘️  Detected Neighborhood Type: {result['neighborhood_type']}")
                print(f"📍 Color: {result['neighborhood_info']['color']}")
                print(f"📝 Description: {result['neighborhood_info']['description']}")
            else:
                print("\n⚠️  Could not determine specific neighborhood type from response")
        else:
            print(f"❌ Analysis failed: {result['error']}")
    else:
        print("❌ example_image.png not found!")
    
    # Test with the generated test images if they exist
    if os.path.exists("test_images/pin_map.png"):
        print("\n\nTesting with pin_map.png...")
        print("-" * 50)
        
        result = agent.analyze("test_images/pin_map.png")
        
        if result["success"]:
            print("✅ Analysis successful!")
            print(f"\nRaw Analysis:\n{result['raw_analysis']}")
            
            if result["neighborhood_type"]:
                print(f"\n🏘️  Detected Neighborhood Type: {result['neighborhood_type']}")
            else:
                print("\n⚠️  Could not determine specific neighborhood type from response")
        else:
            print(f"❌ Analysis failed: {result['error']}")

if __name__ == "__main__":
    main()