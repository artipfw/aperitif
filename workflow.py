import asyncio
import os
from typing import Optional
from agno.openai import OpenAI
from agents.chat_agent import ChatAgent, AddressExtraction
from agents.vision_agent import VisionAgent, ColorExtraction
import json


class MultiAgentWorkflow:
    def __init__(self, openai_api_key: str, azure_api_key: str):
        # Initialize LLM client for chat agent
        self.llm_client = OpenAI(api_key=openai_api_key)
        
        # Initialize agents
        self.chat_agent = ChatAgent(self.llm_client)
        self.vision_agent = VisionAgent(azure_api_key)
        
        self.current_address: Optional[AddressExtraction] = None
        self.screenshots: Optional[dict] = None
    
    async def process_user_message(self, message: str) -> dict:
        """Process user message through the workflow"""
        
        # Step 1: Chat agent processes message and extracts address
        print(f"Processing message: {message}")
        chat_response = await self.chat_agent.run(message)
        
        # Check if we have extracted an address with high confidence
        if hasattr(chat_response, 'address_extraction'):
            self.current_address = chat_response.address_extraction
            
            if self.current_address.confidence > 0.8:
                print(f"Address extracted: {self.current_address.full_address}")
                
                # Step 2: Capture screenshots
                self.screenshots = await self.chat_agent._capture_screenshots(
                    self.current_address.full_address
                )
                
                # Step 3: Send to vision agent for color extraction
                if 'region_map' in self.screenshots and 'pin_map' in self.screenshots:
                    if not isinstance(self.screenshots['region_map'], dict) and \
                       not isinstance(self.screenshots['pin_map'], dict):
                        
                        color_result = await self.vision_agent.analyze(
                            self.screenshots['region_map'],
                            self.screenshots['pin_map']
                        )
                        
                        return {
                            "status": "complete",
                            "address": self.current_address.dict(),
                            "color_extraction": color_result.dict(),
                            "message": f"Address '{self.current_address.full_address}' is located in {color_result.region_name} (color: {color_result.color_name})"
                        }
                
                return {
                    "status": "screenshots_failed",
                    "address": self.current_address.dict(),
                    "message": "Failed to capture screenshots",
                    "errors": self.screenshots
                }
        
        return {
            "status": "needs_more_info",
            "message": chat_response.message if hasattr(chat_response, 'message') else "Please provide more address information"
        }


async def main():
    # Get API keys from environment
    openai_key = os.getenv("OPENAI_API_KEY")
    azure_key = os.getenv("AZURE_API_KEY")
    
    if not openai_key or not azure_key:
        print("Please set OPENAI_API_KEY and AZURE_API_KEY environment variables")
        return
    
    # Create workflow
    workflow = MultiAgentWorkflow(openai_key, azure_key)
    
    # Interactive loop
    print("Multi-Agent Address Color Extraction System")
    print("Type 'quit' to exit")
    print("-" * 50)
    
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() == 'quit':
            break
        
        result = await workflow.process_user_message(user_input)
        print(f"\nSystem: {json.dumps(result, indent=2)}")


if __name__ == "__main__":
    asyncio.run(main())