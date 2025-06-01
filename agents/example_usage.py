#!/usr/bin/env python3
"""
Example usage of the multi-agent system
"""

import os
from conversational_agent import ConversationalAgent

def example_neighborhood_analysis():
    """Example: Analyze a San Francisco neighborhood"""
    
    # Replace with your actual Koyeb endpoint for Qwen
    koyeb_endpoint = "https://your-qwen-endpoint.koyeb.app/v1"
    
    # Initialize the agent
    agent = ConversationalAgent(koyeb_endpoint)
    
    # Have a conversation
    print("🤖 Starting neighborhood analysis...")
    
    # The agent will:
    # 1. Take a Google Maps screenshot (using test image)
    # 2. Take a HoodMaps screenshot (using test image) 
    # 3. Use GPT-4o vision to analyze both images
    response = agent.chat("Can you analyze what type of neighborhood the Mission District in San Francisco is?")
    
    print(f"Agent Response: {response}")

def example_interactive_chat():
    """Example: Interactive chat with the agent"""
    
    koyeb_endpoint = "https://your-qwen-endpoint.koyeb.app/v1"
    agent = ConversationalAgent(koyeb_endpoint)
    
    print("🤖 Interactive Chat (type 'quit' to exit)")
    print("Try asking about SF neighborhoods!")
    
    while True:
        user_input = input("\n👤 You: ")
        if user_input.lower() in ['quit', 'exit', 'bye']:
            break
            
        response = agent.chat(user_input)
        print(f"\n🤖 Agent: {response}")

if __name__ == "__main__":
    print("Choose an example:")
    print("1. Neighborhood analysis")
    print("2. Interactive chat")
    
    choice = input("Enter choice (1 or 2): ")
    
    if choice == "1":
        example_neighborhood_analysis()
    elif choice == "2":
        example_interactive_chat()
    else:
        print("Invalid choice")