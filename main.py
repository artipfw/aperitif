#!/usr/bin/env python3
"""
Main interface for the multi-agent San Francisco neighborhood analysis system
"""

import sys
from agents.conversational_agent import ConversationalAgent

def main():
    if len(sys.argv) > 1:
        if sys.argv[1] == "--conversation":
            test_conversation()
        elif sys.argv[1] == "--vision":
            test_vision()
        else:
            print("Usage: python main.py [--conversation|--vision]")
            print("  --conversation: Test DeepSeek R1 conversational agent")
            print("  --vision: Test GPT-4o vision analysis with SF images")
    else:
        interactive_mode()

def test_conversation():
    print("Testing DeepSeek R1 conversational agent...")
    
    try:
        agent = ConversationalAgent(demo_mode=True)
        test_prompt = "Can you analyze what type of neighborhood the Mission District is in San Francisco?"
        
        print(f"User: {test_prompt}")
        response = agent.chat(test_prompt)
        print(f"Agent: {response}")
        
    except Exception as e:
        print(f"Error: {e}")

def test_vision():
    print("Testing GPT-4o vision analysis with SF test images...")
    
    try:
        from agents.vision_agent import VisionAgent
        
        vision_agent = VisionAgent(use_openai=True)
        
        # Use test images
        pin_map = "/Users/home/aperitif/test_images/sf_map_with_pin.png"
        region_map = "/Users/home/aperitif/test_images/region_map.png"
        
        print(f"Analyzing: {pin_map} vs {region_map}")
        result = vision_agent.analyze_with_reference(region_map, pin_map)
        
        if result['success']:
            print(f"Neighborhood type: {result.get('neighborhood_type', 'Unknown')}")
            print(f"Analysis: {result.get('raw_analysis', 'No analysis')}")
        else:
            print(f"Vision analysis failed: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"Error: {e}")

def interactive_mode():
    print("SF Neighborhood Analysis System")
    print("Usage: python main.py [--conversation|--vision]")
    
    try:
        agent = ConversationalAgent()
        print("Interactive mode (type 'quit' to exit)")
        
        while True:
            user_input = input("\nYou: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'bye']:
                break
                
            if not user_input:
                continue
            
            response = agent.chat(user_input)
            print(f"Agent: {response}")
            
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()