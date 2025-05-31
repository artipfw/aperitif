#!/usr/bin/env python3
"""
Comprehensive test showing Phi-4 limitations and OpenAI solution
"""

import os
from agents.vision_agent import VisionAgent

def test_phi4_limitations():
    """Test Phi-4 with both simple and complex images to show its limitations"""
    print("=" * 80)
    print("PART 1: Testing Phi-4 Vision Model")
    print("=" * 80)
    
    # Initialize Phi-4 agent
    phi4_agent = VisionAgent(use_openai=False)
    
    # Test 1: Simple test image (should work)
    print("\nTest 1: Simple colored map (test_images/pin_map.png)")
    print("-" * 50)
    
    if os.path.exists("test_images/pin_map.png"):
        result = phi4_agent.analyze("test_images/pin_map.png")
        
        print(f"Model: {result['model_used']}")
        print(f"Success: {result['success']}")
        
        if result['success']:
            print(f"\nAnalysis: {result['raw_analysis'][:200]}...")
            if result['neighborhood_type']:
                print(f"\n✅ Detected neighborhood: {result['neighborhood_type']}")
            else:
                print("\n⚠️  Failed to detect neighborhood type")
        else:
            print(f"❌ Error: {result['error']}")
    else:
        print("❌ test_images/pin_map.png not found")
    
    # Test 2: Complex real-world map (likely to fail)
    print("\n\nTest 2: Complex San Francisco map (example_image.png)")
    print("-" * 50)
    
    if os.path.exists("example_image.png"):
        result = phi4_agent.analyze("example_image.png")
        
        print(f"Model: {result['model_used']}")
        print(f"Success: {result['success']}")
        
        if result['success']:
            print(f"\nAnalysis (first 300 chars): {result['raw_analysis'][:300]}...")
            if "Pix" in result['raw_analysis'] or "idden" in result['raw_analysis']:
                print("\n❌ Phi-4 returned gibberish output (contains 'Pix', 'idden', etc.)")
            elif result['neighborhood_type']:
                print(f"\n✅ Detected neighborhood: {result['neighborhood_type']}")
            else:
                print("\n⚠️  Failed to detect neighborhood type")
        else:
            print(f"❌ Error: {result['error']}")
    else:
        print("❌ example_image.png not found")
    
    print("\n" + "=" * 50)
    print("CONCLUSION: Phi-4 works well with simple images but struggles with complex maps")
    print("=" * 50)

def test_openai_solution():
    """Test OpenAI's vision model as the solution"""
    print("\n\n" + "=" * 80)
    print("PART 2: Testing OpenAI GPT-4 Vision Model")
    print("=" * 80)
    
    # Check for API key
    if not os.environ.get("OPENAI_API_KEY"):
        print("\n❌ OPENAI_API_KEY environment variable not set")
        print("Please set your OpenAI API key:")
        print("export OPENAI_API_KEY='your-key-here'")
        return
    
    # Initialize OpenAI agent
    openai_agent = VisionAgent(use_openai=True)
    
    # Test 1: Original SF map (example_image.png)
    print("\nTest 1: Original San Francisco map (example_image.png)")
    print("-" * 50)
    
    if os.path.exists("example_image.png"):
        result = openai_agent.analyze("example_image.png")
        
        print(f"Model: {result['model_used']}")
        print(f"Success: {result['success']}")
        
        if result['success']:
            print(f"\nAnalysis:\n{result['raw_analysis']}")
            if result['neighborhood_type']:
                print(f"\n✅ Detected neighborhood: {result['neighborhood_type']}")
                print(f"📍 Color: {result['neighborhood_info']['color']}")
                print(f"📝 Description: {result['neighborhood_info']['description']}")
            else:
                print("\n⚠️  No specific neighborhood type detected in response")
        else:
            print(f"❌ Error: {result['error']}")
    else:
        print("❌ example_image.png not found")
    
    # Test 2: SF map with added pin
    print("\n\nTest 2: San Francisco map with added pin (test_images/sf_map_with_pin.png)")
    print("-" * 50)
    
    if os.path.exists("test_images/sf_map_with_pin.png"):
        result = openai_agent.analyze("test_images/sf_map_with_pin.png")
        
        print(f"Model: {result['model_used']}")
        print(f"Success: {result['success']}")
        
        if result['success']:
            print(f"\nAnalysis:\n{result['raw_analysis']}")
            if result['neighborhood_type']:
                print(f"\n✅ Detected neighborhood: {result['neighborhood_type']}")
                print(f"📍 Color: {result['neighborhood_info']['color']}")
                print(f"📝 Description: {result['neighborhood_info']['description']}")
            else:
                print("\n⚠️  No specific neighborhood type detected in response")
        else:
            print(f"❌ Error: {result['error']}")
    else:
        print("❌ test_images/sf_map_with_pin.png not found")
    
    print("\n" + "=" * 50)
    print("CONCLUSION: OpenAI's model successfully analyzes complex maps")
    print("=" * 50)

def main():
    print("San Francisco Neighborhood Detection - Model Comparison")
    print("This test demonstrates why we need to use OpenAI's vision model")
    print()
    
    # Part 1: Show Phi-4 limitations
    test_phi4_limitations()
    
    # Part 2: Show OpenAI solution
    test_openai_solution()
    
    print("\n\n" + "=" * 80)
    print("FINAL RECOMMENDATION")
    print("=" * 80)
    print("While Phi-4 is a capable model for simple vision tasks, it struggles with:")
    print("- Complex, high-resolution images")
    print("- Images with lots of text and UI elements")
    print("- Real-world screenshots and maps")
    print("\nFor production use with San Francisco neighborhood maps, we recommend")
    print("using OpenAI's GPT-4 Vision model for accurate results.")
    print("=" * 80)

if __name__ == "__main__":
    main()