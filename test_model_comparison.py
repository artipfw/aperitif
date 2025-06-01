#!/usr/bin/env python3
"""
Test vision agents' ability to map pins between uncolored and colored maps
"""

import os
import argparse
from agents.vision_agent import VisionAgent

def display_result(result, test_name):
    """Display analysis results in a clean, presentation-ready format"""
    print(f"\n🤖 Model: {result['model_used']}")
    print(f"🔍 Method: {result.get('method', 'two-image-comparison')}")
    print(f"✨ Success: {'✅ Yes' if result['success'] else '❌ No'}")
    
    if result['success']:
        print(f"\n📊 ANALYSIS RESULTS:")
        print(f"{result['raw_analysis']}")
        
        if result['neighborhood_type']:
            print(f"\n🎯 FINAL CLASSIFICATION:")
            print(f"   Neighborhood: {result['neighborhood_type']}")
            print(f"   Color Zone: {result['neighborhood_info']['color']}")
            print(f"   Description: {result['neighborhood_info']['description']}")
            print(f"   Test: {test_name} ✅")
        else:
            print(f"\n⚠️  Could not determine specific neighborhood type")
    else:
        print(f"\n❌ Error: {result['error']}")
    
    print()

def test_phi4_pin_mapping():
    """Test Phi-4's ability to map pins between images"""
    print("=" * 80)
    print("🚀 Testing Phi-4 Vision Model - Pin Mapping")
    print("=" * 80)
    
    # Initialize Phi-4 agent
    phi4_agent = VisionAgent(use_openai=False)
    
    print("\n🗺️  PHI-4 TEST: San Francisco Map Analysis")
    print("Pin location: Painted Ladies area")
    print("-" * 60)
    
    pin_map_path = "test_images/sf_map_with_pin.png"
    colored_map_path = "test_images/sf_map_original.png"
    
    print(f"📍 Pin map: {pin_map_path}")
    print(f"🎨 Reference map: {colored_map_path}")
    
    if os.path.exists(pin_map_path) and os.path.exists(colored_map_path):
        result = phi4_agent.analyze_with_reference(pin_map_path, colored_map_path)
        display_result(result, "Phi-4 SF Analysis")
    else:
        print("❌ Required test images not found")
    
    print("\n" + "=" * 50)

def test_openai_pin_mapping():
    """Test OpenAI's ability to map pins between uncolored and colored maps"""
    print("\n\n" + "=" * 80)
    print("🤖 Testing OpenAI GPT-4 Vision Model - Pin Mapping")
    print("=" * 80)
    
    # Check for API key
    if not os.environ.get("OPENAI_API_KEY"):
        print("\n❌ OPENAI_API_KEY environment variable not set")
        print("Please set your OpenAI API key:")
        print("export OPENAI_API_KEY='your-key-here'")
        return
    
    # Initialize OpenAI agent
    openai_agent = VisionAgent(use_openai=True)
    
    # Test 1: SF Map with Painted Ladies Pin
    print("\n🗺️  TEST 1: San Francisco Map Analysis")
    print("Pin location: Painted Ladies area")
    print("-" * 60)
    
    pin_map_path = "test_images/sf_map_with_pin.png"
    colored_map_path = "test_images/sf_map_original.png"
    
    print(f"📍 Pin map: {pin_map_path}")
    print(f"🎨 Reference map: {colored_map_path}")
    
    if os.path.exists(pin_map_path) and os.path.exists(colored_map_path):
        result = openai_agent.analyze_with_reference(pin_map_path, colored_map_path)
        display_result(result, "SF Painted Ladies")
    else:
        print("❌ Required images not found")
    
    print("\n" + "="*60)
    
    # # Test 2: General Pin Map and Region Map
    # print("\n🗺️  TEST 2: Generic Pin Map Analysis") 
    # print("Testing with different pin/region map pair")
    # print("-" * 60)
    
    # pin_map_path2 = "test_images/pin_map.png"
    # region_map_path = "test_images/region_map.png"
    
    # print(f"📍 Pin map: {pin_map_path2}")
    # print(f"🎨 Reference map: {region_map_path}")
    
    # if os.path.exists(pin_map_path2) and os.path.exists(region_map_path):
    #     result = openai_agent.analyze_with_reference(pin_map_path2, region_map_path)
    #     display_result(result, "Generic Pin Map")
    # else:
    #     print("❌ Required images not found")
    


def main():
    parser = argparse.ArgumentParser(
        description="🗺️  Test vision models' ability to map pins between colored and uncolored maps"
    )
    parser.add_argument(
        "--skip-phi", 
        action="store_true", 
        help="Skip Phi-4 model tests and only run OpenAI tests"
    )
    parser.add_argument(
        "--only-phi",
        action="store_true",
        help="Only run Phi-4 model tests"
    )
    
    args = parser.parse_args()
    
    print("🌟 VISION MODEL COMPARISON - PIN MAPPING TEST")
    print("🎯 Testing ability to map pins between uncolored and colored maps")
    print("📍 Using San Francisco neighborhood data")
    print()
    
    # Run tests based on arguments
    if args.only_phi:
        test_phi4_pin_mapping()
    elif args.skip_phi:
        test_openai_pin_mapping()
    else:
        # Run both by default
        test_phi4_pin_mapping()
        test_openai_pin_mapping()
    
    if not args.only_phi:
        print("\n\n" + "=" * 80)
        print("📊 SUMMARY & CAPABILITIES")
        print("=" * 80)
        print("✨ This test evaluates models' ability to:")
        print("   🔍 1. Identify pin locations in maps")
        print("   🎨 2. Map locations to colored neighborhood zones")
        print("   🏠 3. Classify neighborhood types accurately")
        print("   📐 4. Handle different map scales and formats")
        print("=" * 80)

if __name__ == "__main__":
    main()