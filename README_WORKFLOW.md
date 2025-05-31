# Multi-Agent Address Color Extraction Workflow

This system uses multiple AI agents to extract addresses from conversations and analyze map screenshots.

## Architecture

### 1. Chat Agent (`agents/chat_agent.py`)
- **Purpose**: Extract addresses from natural conversation
- **Model**: Uses OpenAI GPT-4o for conversation and address extraction
- **Tools**: 
  - `capture_region_map`: Go tool that captures colored region map with legend
  - `capture_pin_map`: Go tool that captures map with pin at address location

### 2. Vision Agent (`agents/vision_agent.py`)
- **Purpose**: Analyze screenshots to extract color at pin location
- **Model**: microsoft/Phi-4-multimodal-instruct (via Azure)
- **Input**: Two base64-encoded images (region map and pin map)
- **Output**: Color information and region name

### 3. Go Tools
- **capture_region_map**: Generates map with colored regions and legend
- **capture_pin_map**: Generates map with pin at specified address

## Workflow

1. User provides address information through conversation
2. Chat agent extracts and validates the address
3. Once confident (>80%), triggers screenshot capture tools
4. Vision agent analyzes both images to:
   - Locate the pin position
   - Extract color at that location from region map
   - Match color to legend to identify region

## Setup

1. Install dependencies:
```bash
uv sync
```

2. Build Go tools:
```bash
go build -o tools/capture_region_map tools/capture_region_map/main.go
go build -o tools/capture_pin_map tools/capture_pin_map/main.go
chmod +x tools/capture_region_map tools/capture_pin_map
```

3. Set environment variables:
```bash
export OPENAI_API_KEY="your-key"
export AZURE_API_KEY="your-azure-key"
```

## Usage

### Interactive Mode
```bash
python workflow.py
```

### Programmatic Usage
```python
from workflow import MultiAgentWorkflow

workflow = MultiAgentWorkflow(openai_key, azure_key)
result = await workflow.process_user_message("123 Main St, San Francisco")
```

## Response Format

```json
{
  "status": "complete",
  "address": {
    "street": "123 Main Street",
    "city": "San Francisco",
    "state": "CA",
    "country": "USA",
    "full_address": "123 Main Street, San Francisco, CA 94105",
    "confidence": 0.95
  },
  "color_extraction": {
    "color_name": "Blue",
    "rgb_values": [0, 100, 200],
    "hex_value": "#0064C8",
    "region_name": "District A",
    "confidence": 0.95
  },
  "message": "Address '123 Main Street, San Francisco, CA 94105' is located in District A (color: Blue)"
}
```

## Notes

- The Go tools are placeholders and need actual implementation for map generation
- The vision agent expects specific image formats (PNG with clear legends)
- Address extraction works best with complete, well-formatted addresses