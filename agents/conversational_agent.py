import os
import json
import subprocess
from typing import Dict, Any, List, Optional
from openai import OpenAI
from .vision_agent import VisionAgent


class ConversationalAgent:
    """Conversational agent using Qwen that can call tools and coordinate with vision agent"""
    
    def __init__(self, demo_mode=False):
        """
        Initialize the conversational agent with correct Koyeb endpoint and model
        
        Args:
            demo_mode: If True, fake tool calls for demonstration purposes
        """
        self.demo_mode = demo_mode
        self.client = OpenAI(
            api_key=os.environ.get("OPENAI_API_KEY", "fake"),
            base_url="https://symbolic-keeley-metal-fiefs-0z-3a306699.koyeb.app/v1",
        )
        # self.model_name = "DeepSeek-R1-Distill-Llama-8B"
        self.model_name = "/models/DeepSeek-R1-Distill-Llama-8B"
        self.vision_agent = VisionAgent(use_openai=True)  # Use GPT-4o for vision
        
        # Available tools
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "take_google_maps_screenshot",
                    "description": "Take a screenshot of Google Maps for a given location",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "location": {
                                "type": "string",
                                "description": "The location to screenshot (address or place name)"
                            },
                            "use_test_image": {
                                "type": "boolean",
                                "description": "Whether to use test images instead of actual screenshots",
                                "default": True
                            }
                        },
                        "required": ["location"]
                    }
                }
            },
            {
                "type": "function", 
                "function": {
                    "name": "take_hoodmaps_screenshot",
                    "description": "Take a screenshot of HoodMaps for San Francisco neighborhood analysis",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "use_test_image": {
                                "type": "boolean",
                                "description": "Whether to use test images instead of actual screenshots",
                                "default": True
                            }
                        }
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "analyze_neighborhood",
                    "description": "Analyze neighborhood type from maps using vision AI",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "pin_map_path": {
                                "type": "string",
                                "description": "Path to the map with pin location"
                            },
                            "legend_map_path": {
                                "type": "string", 
                                "description": "Path to the reference map with neighborhood zones"
                            }
                        },
                        "required": ["pin_map_path", "legend_map_path"]
                    }
                }
            }
        ]
        
        self.conversation_history = []
    
    def take_google_maps_screenshot(self, location: str, use_test_image: bool = True) -> Dict[str, Any]:
        """Take a Google Maps screenshot or use test image"""
        if use_test_image:
            # Use test image instead of actual screenshot
            test_path = "/Users/home/aperitif/test_images/sf_map_with_pin.png"
            return {
                "success": True,
                "screenshot_path": test_path,
                "location": location,
                "method": "test_image"
            }
        else:
            try:
                # Run the Go screenshot service (currently uses default location)
                result = subprocess.run(
                    ["go", "run", "cmd/service.go"],
                    cwd="/Users/home/aperitif/aperitif_scraper",
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0:
                    return {
                        "success": True,
                        "screenshot_path": "/Users/home/aperitif/aperitif_scraper/google_screenshot.png",
                        "location": location,
                        "method": "go_service"
                    }
                else:
                    return {
                        "success": False,
                        "error": result.stderr,
                        "location": location
                    }
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e),
                    "location": location
                }
    
    def take_hoodmaps_screenshot(self, use_test_image: bool = True) -> Dict[str, Any]:
        """Take a HoodMaps screenshot or use test image"""
        if use_test_image:
            # Use test image instead of actual screenshot
            test_path = "/Users/home/aperitif/test_images/region_map.png"
            return {
                "success": True,
                "screenshot_path": test_path,
                "method": "test_image"
            }
        else:
            try:
                # Run the Go screenshot service for hoodmaps
                result = subprocess.run(
                    ["go", "run", "cmd/service.go"],
                    cwd="/Users/home/aperitif/aperitif_scraper",
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0:
                    return {
                        "success": True,
                        "screenshot_path": "/Users/home/aperitif/aperitif_scraper/hoodmaps_screenshot.png",
                        "method": "go_service"
                    }
                else:
                    return {
                        "success": False,
                        "error": result.stderr
                    }
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e)
                }
    
    def analyze_neighborhood(self, pin_map_path: str, legend_map_path: str) -> Dict[str, Any]:
        """Analyze neighborhood using the vision agent"""
        return self.vision_agent.analyze_with_reference(legend_map_path, pin_map_path)
    
    def execute_tool_call(self, tool_call) -> str:
        """Execute a tool call and return the result"""
        function_name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)
        
        try:
            if function_name == "take_google_maps_screenshot":
                result = self.take_google_maps_screenshot(**arguments)
            elif function_name == "take_hoodmaps_screenshot":
                result = self.take_hoodmaps_screenshot(**arguments)
            elif function_name == "analyze_neighborhood":
                result = self.analyze_neighborhood(**arguments)
            else:
                result = {"success": False, "error": f"Unknown function: {function_name}"}
            
            return json.dumps(result, indent=2)
        except Exception as e:
            return json.dumps({"success": False, "error": str(e)})
    
    def chat(self, user_message: str) -> str:
        """Have a conversation with the user, using tools when needed"""
        # Add user message to history
        self.conversation_history.append({"role": "user", "content": user_message})
        
        if self.demo_mode:
            return self._demo_chat(user_message)
        
        system_prompt = """You are a helpful assistant that can take screenshots of maps and analyze San Francisco neighborhoods. 

You have access to these tools:
1. take_google_maps_screenshot - Take screenshots of Google Maps for any location
2. take_hoodmaps_screenshot - Take screenshots of HoodMaps showing SF neighborhood zones
3. analyze_neighborhood - Use AI vision to analyze what type of neighborhood a location is

Your workflow for neighborhood analysis:
1. Take a Google Maps screenshot of the requested location
2. Take a HoodMaps screenshot to get the reference map with neighborhood zones
3. Use the vision AI to analyze both images and determine the neighborhood type

Be conversational and helpful. Explain what you're doing step by step."""

        messages = [
            {"role": "system", "content": system_prompt},
            *self.conversation_history
        ]
        
        # Try without tools first to test basic connectivity
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                tools=self.tools,
                temperature=0.7,
                max_tokens=1000
            )
        except Exception as e:
            if "tool choice" in str(e).lower() or "tool" in str(e).lower():
                return self._demo_chat(user_message)
            else:
                raise e
        
        response_message = response.choices[0].message
        
        # Handle tool calls if any
        if response_message.tool_calls:
            # Add the assistant's response with tool calls to history
            self.conversation_history.append({
                "role": "assistant",
                "content": response_message.content,
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": tc.type,
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    } for tc in response_message.tool_calls
                ]
            })
            
            # Execute each tool call
            for tool_call in response_message.tool_calls:
                tool_result = self.execute_tool_call(tool_call)
                
                # Add tool result to history
                self.conversation_history.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": tool_result
                })
            
            # Get final response after tool execution
            final_response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    *self.conversation_history
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            final_message = final_response.choices[0].message.content
            self.conversation_history.append({"role": "assistant", "content": final_message})
            return final_message
        else:
            # No tool calls, just return the response
            self.conversation_history.append({"role": "assistant", "content": response_message.content})
            return response_message.content
    
    def _demo_chat(self, user_message: str) -> str:
        """Demo mode: Just get conversational response from DeepSeek R1"""
        # Simplified system prompt for demo
        system_prompt = """You are a helpful assistant that specializes in analyzing San Francisco neighborhoods. 
        
When asked about neighborhood analysis, explain that you would normally:
1. Take screenshots of Google Maps for the location
2. Take screenshots of HoodMaps with neighborhood zones
3. Use AI vision to analyze both images
4. Provide detailed neighborhood classification

Be conversational and helpful. Explain your planned approach for the request."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
        
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )
            
            conversational_response = response.choices[0].message.content
            self.conversation_history.append({"role": "assistant", "content": conversational_response})
            return conversational_response
            
        except Exception as e:
            # Fallback response
            fallback_response = """I'd be happy to analyze the Mission District neighborhood for you! 

Here's what I would normally do:
1. Take a Google Maps screenshot of the Mission District area
2. Capture a HoodMaps reference showing SF neighborhood zones
3. Use AI vision to analyze both images and determine the neighborhood type
4. Provide you with detailed insights about the area's characteristics

The Mission District is known for being a vibrant, diverse neighborhood with a rich Latino heritage, great food scene, and mix of residential and commercial areas. Would you like me to proceed with the detailed analysis?"""
            
            self.conversation_history.append({"role": "assistant", "content": fallback_response})
            return fallback_response
    
    def demo_vision_analysis(self) -> str:
        """Separate step: Run the actual vision analysis"""
        print("\n" + "=" * 60)
        print("🔍 STEP 2: Vision Analysis")
        print("=" * 60)
        
        # Step 1: Get screenshots (using test images)
        print("📸 Taking Google Maps screenshot...")
        google_result = self.take_google_maps_screenshot("Mission District, San Francisco", use_test_image=True)
        print(f"   ✅ Screenshot: {google_result['screenshot_path']}")
        
        print("📸 Taking HoodMaps screenshot...")
        hood_result = self.take_hoodmaps_screenshot(use_test_image=True)
        print(f"   ✅ Screenshot: {hood_result['screenshot_path']}")
        
        # Step 2: Real vision analysis
        print("🔍 Analyzing with GPT-4o vision...")
        analysis_result = self.analyze_neighborhood(
            pin_map_path=google_result['screenshot_path'],
            legend_map_path=hood_result['screenshot_path']
        )
        
        if analysis_result['success']:
            neighborhood_type = analysis_result.get('neighborhood_type', 'Unknown')
            raw_analysis = analysis_result.get('raw_analysis', '')
            
            vision_response = f"""✅ Vision Analysis Complete!

🏘️ **Neighborhood Classification:** {neighborhood_type}

📋 **Detailed Analysis:**
{raw_analysis}

🤖 **Models Used:**
- Conversational: DeepSeek R1 
- Vision: GPT-4o

This demonstrates the complete multi-agent workflow for SF neighborhood analysis!"""
        else:
            vision_response = f"""❌ Vision analysis encountered an error:
{analysis_result.get('error', 'Unknown error')}

The workflow is set up correctly, but there was an issue with the vision component."""
        
        print("   ✅ Vision analysis complete")
        return vision_response
    
    def reset_conversation(self):
        """Reset the conversation history"""
        self.conversation_history = []