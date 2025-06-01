# Aperitif - SF Neighborhood Analysis

Multi-agent system for analyzing San Francisco neighborhoods using map screenshots and AI vision.

## Architecture

- **Conversational Agent**: DeepSeek R1 for natural language interaction
- **Vision Agent**: GPT-4o for analyzing map images and neighborhood classification
- **Screenshot Tools**: Go programs for capturing Google Maps and HoodMaps

## Usage

```bash
# Test conversational agent (DeepSeek R1)
uv run python main.py --conversation

# Test vision analysis (GPT-4o with SF images)
uv run python main.py --vision

# Interactive mode
uv run python main.py

# Tool calling example (latest demo)
uv run python tool_calling.py
```

## Components

### `/agents/`
- `conversational_agent.py` - DeepSeek R1 agent with tool calling
- `vision_agent.py` - GPT-4o vision analysis for neighborhood classification

### `/aperitif_scraper/`
- Go programs for taking map screenshots
- `cmd/service.go` - Main service entry point
- `googlemap/` - Google Maps screenshot client
- `hoodmap/` - HoodMaps screenshot client

### `/test_images/`
- Sample SF map images for testing
- `sf_map_with_pin.png` - Google Maps with location pin
- `region_map.png` - HoodMaps with neighborhood zones

## Model Evaluation

### Vision Model Comparison

We tested multiple vision models to determine the best fit for pin mapping and neighborhood classification:

```bash
# Test both Phi-4 and GPT-4o vision models
uv run python test_model_comparison.py

# Test only Phi-4 (local model)
uv run python test_model_comparison.py --only-phi

# Test only GPT-4o (requires OpenAI API key)
uv run python test_model_comparison.py --skip-phi
```

The test evaluates models' ability to:
- Identify pin locations in uncolored maps
- Map locations to colored neighborhood zones  
- Classify neighborhood types accurately
- Handle different map scales and formats

**Results**: GPT-4o demonstrated superior performance for complex spatial reasoning and neighborhood classification, while Phi-4 showed promise as a cost-effective alternative for simpler mapping tasks.

## Configuration

Set your endpoints in `agents/conversational_agent.py`:
- Koyeb endpoint for DeepSeek R1
- OpenAI API key for GPT-4o vision