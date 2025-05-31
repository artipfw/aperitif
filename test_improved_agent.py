#!/usr/bin/env python3
"""Test the improved vision agent"""

import os
from agents.vision_agent_improved import ImprovedVisionAgent
from agents.vision_agent import VisionAgent

def main():
    print("Testing Improved Vision Agent")
    print("=" * 50)
    
    # Test with improved agent
    improved_agent = ImprovedVisionAgent()
    
    if os.path.exists("example_image.png"):
        print("\nTesting with ImprovedVisionAgent...")
        print("-" * 50)
        
        result = improved_agent.analyze("example_image.png")
        
        if result["success"]:
            print("✅ Analysis successful!")
            print(f"\nStep-by-step analysis:")
            print(result['raw_analysis'])
            
            if result["neighborhood_type"]:
                print(f"\n🏘️  Detected Neighborhood Type: {result['neighborhood_type']}")
                print(f"📍 Color: {result['neighborhood_info']['color']}")
                print(f"📝 Description: {result['neighborhood_info']['description']}")
            else:
                print("\n⚠️  Could not determine specific neighborhood type")
                
            if 'metadata' in result:
                print(f"\n📊 Image metadata:")
                print(f"   Original size: {result['metadata'].get('original_size', 'N/A')}")
                print(f"   Processed size: {result['metadata'].get('processed_size', 'N/A')}")
                print(f"   File size: {result['metadata'].get('file_size_kb', 'N/A'):.1f} KB")
        else:
            print(f"❌ Analysis failed: {result['error']}")
    
    # Compare with original agent on test image
    if os.path.exists("test_images/pin_map.png"):
        print("\n\nComparing agents on test_images/pin_map.png...")
        print("-" * 50)
        
        # Original agent
        print("\nOriginal VisionAgent:")
        original_agent = VisionAgent()
        result1 = original_agent.analyze("test_images/pin_map.png")
        if result1["success"] and result1["neighborhood_type"]:
            print(f"✅ Detected: {result1['neighborhood_type']}")
        else:
            print("❌ Failed to detect")
        
        # Improved agent
        print("\nImproved VisionAgent:")
        result2 = improved_agent.analyze("test_images/pin_map.png")
        if result2["success"] and result2["neighborhood_type"]:
            print(f"✅ Detected: {result2['neighborhood_type']}")
        else:
            print("❌ Failed to detect")

if __name__ == "__main__":
    main()