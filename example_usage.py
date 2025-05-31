import asyncio
import os
from workflow import MultiAgentWorkflow


async def test_workflow():
    """Test the multiagent workflow with a sample address"""
    
    # Set up API keys (in production, use environment variables)
    openai_key = os.getenv("OPENAI_API_KEY", "your-openai-key")
    azure_key = os.getenv("AZURE_API_KEY", "your-azure-key")
    
    # Create workflow
    workflow = MultiAgentWorkflow(openai_key, azure_key)
    
    # Test messages
    test_messages = [
        "I'm looking for information about 123 Main Street",
        "It's in San Francisco, California",
        "The full address is 123 Main Street, San Francisco, CA 94105"
    ]
    
    for message in test_messages:
        print(f"\nUser: {message}")
        result = await workflow.process_user_message(message)
        print(f"System Response: {result}")
        
        if result.get("status") == "complete":
            print("\n✅ Successfully extracted color at address location!")
            print(f"Address: {result['address']['full_address']}")
            print(f"Color: {result['color_extraction']['color_name']} ({result['color_extraction']['hex_value']})")
            print(f"Region: {result['color_extraction']['region_name']}")
            break


if __name__ == "__main__":
    print("Testing Multi-Agent Workflow...")
    asyncio.run(test_workflow())