from agno import Agent
from agno.agent import Callable, Input, Response
from agno.openai import OpenAI
from pydantic import BaseModel, Field
from typing import Optional, List
import asyncio
import subprocess
import base64
from pathlib import Path


class AddressExtraction(BaseModel):
    """Extracted address information"""
    street: Optional[str] = Field(None, description="Street name and number")
    city: Optional[str] = Field(None, description="City name")
    state: Optional[str] = Field(None, description="State or province")
    country: Optional[str] = Field(None, description="Country")
    full_address: str = Field(..., description="Complete address string")
    confidence: float = Field(..., description="Confidence level 0-1")


class ScreenshotTool(BaseModel):
    """Tool for taking screenshots"""
    name: str = Field(..., description="Tool name")
    command: str = Field(..., description="Go command to execute")
    
    async def execute(self, address: str) -> str:
        """Execute the Go tool and return base64 encoded image"""
        try:
            result = subprocess.run(
                [self.command, address],
                capture_output=True,
                text=True,
                check=True
            )
            
            # Assuming the Go tool saves to a specific path
            image_path = Path(f"./screenshots/{self.name}_{address.replace(' ', '_')}.png")
            if image_path.exists():
                with open(image_path, "rb") as f:
                    return base64.b64encode(f.read()).decode()
            else:
                raise FileNotFoundError(f"Screenshot not found at {image_path}")
                
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Tool {self.name} failed: {e.stderr}")


class ChatAgent:
    def __init__(self, llm_client: OpenAI):
        self.llm = llm_client
        self.tools = [
            ScreenshotTool(name="region_map", command="./tools/capture_region_map"),
            ScreenshotTool(name="pin_map", command="./tools/capture_pin_map")
        ]
        
        self.agent = Agent(
            name="address_extractor",
            model=self.llm,
            instructions="""
            You are a helpful assistant that extracts addresses from user conversations.
            Your goal is to:
            1. Engage in natural conversation to understand what address the user is referring to
            2. Extract and validate the complete address
            3. Once you have a confident address, capture screenshots using the available tools
            
            Be conversational but focused on getting the address information.
            Ask clarifying questions if needed.
            """,
            callables=[self._extract_address, self._capture_screenshots]
        )
    
    @Callable
    async def _extract_address(self, user_message: str) -> AddressExtraction:
        """Extract address from user message"""
        # This would use the LLM to parse and extract address
        response = await self.llm.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Extract address information from the user message. Return structured data."},
                {"role": "user", "content": user_message}
            ],
            response_model=AddressExtraction
        )
        return response
    
    @Callable
    async def _capture_screenshots(self, address: str) -> dict:
        """Capture screenshots for the given address"""
        results = {}
        
        for tool in self.tools:
            try:
                image_data = await tool.execute(address)
                results[tool.name] = image_data
            except Exception as e:
                results[tool.name] = {"error": str(e)}
        
        return results
    
    async def run(self, message: str) -> Response:
        """Process user message and return response"""
        return await self.agent.run(Input(message=message))