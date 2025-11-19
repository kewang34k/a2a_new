# Setup Instructions for LLM-Enhanced Multi-Agent System

## Quick Start

### Option 1: Use Without LLM (No API Key Required)

The system works perfectly fine without an API key using rule-based intent detection:

```python
# In Jupyter/Colab, just run the notebook cells as-is
# The system will automatically fall back to rule-based mode
```

### Option 2: Use With OpenAI LLM (Recommended)

For intelligent, context-aware responses powered by GPT models:

#### Step 1: Get an OpenAI API Key

1. Go to [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)
2. Sign up or log in
3. Click "Create new secret key"
4. Copy your API key (starts with `sk-...`)

#### Step 2: Set Your API Key

**In Google Colab:**
```python
import os
os.environ['OPENAI_API_KEY'] = 'sk-your-api-key-here'
```

**In Jupyter Notebook (Local):**

Create a `.env` file in the project directory:
```bash
# .env file
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_MODEL=gpt-4o-mini  # or gpt-4o for best results
```

Or set it in code:
```python
from config import get_config
config = get_config()
config.set_api_key('sk-your-api-key-here')
```

**In Terminal (Linux/Mac):**
```bash
export OPENAI_API_KEY='sk-your-api-key-here'
```

**In Terminal (Windows):**
```cmd
set OPENAI_API_KEY=sk-your-api-key-here
```

#### Step 3: Install Dependencies

```bash
pip install openai python-dotenv
```

Or install all requirements:
```bash
pip install -r requirements.txt
```

## Running the System

### With LLM (Requires API Key):

```python
from a2a_system_llm import A2ACoordinationSystemLLM

# Initialize with LLM enabled
system = A2ACoordinationSystemLLM("support.db", use_llm=True)

# Process a query
result = system.process_query("I need help upgrading my account, customer ID 5")
print(result['response'])
```

### Without LLM (No API Key):

```python
from a2a_system_llm import A2ACoordinationSystemLLM

# Initialize with LLM disabled (rule-based fallback)
system = A2ACoordinationSystemLLM("support.db", use_llm=False)

# Process a query
result = system.process_query("Get customer information for ID 5")
print(result['response'])
```

## Model Options

| Model | Speed | Quality | Cost | Best For |
|-------|-------|---------|------|----------|
| `gpt-4o-mini` | ⚡⚡⚡ Fast | ✅ Good | 💰 Cheap | Development, Testing |
| `gpt-4o` | ⚡⚡ Medium | ✅✅✅ Excellent | 💰💰 Moderate | Production |
| `gpt-4-turbo` | ⚡ Slower | ✅✅ Very Good | 💰💰💰 Expensive | Complex queries |

**Recommended**: Start with `gpt-4o-mini` for development and testing.

## Features Comparison

| Feature | Rule-Based | LLM-Powered |
|---------|------------|-------------|
| Intent Detection | Pattern matching | Natural language understanding |
| Response Quality | Template-based | Dynamic, contextual |
| Handles Novel Queries | ❌ No | ✅ Yes |
| Cost | Free | ~$0.15-0.60 per 1M tokens |
| Speed | ⚡⚡⚡ Very Fast | ⚡⚡ Fast |
| Accuracy | ~70-80% | ~90-95% |
| API Key Required | ❌ No | ✅ Yes |

## Troubleshooting

### Error: "OpenAI API key not configured"

**Solution**: Set your API key using one of the methods above, or disable LLM:
```python
system = A2ACoordinationSystemLLM("support.db", use_llm=False)
```

### Error: "openai module not found"

**Solution**: Install the OpenAI package:
```bash
pip install openai>=1.0.0
```

### System Falls Back to Rule-Based Mode

This happens when:
- No API key is set
- API key is invalid
- OpenAI package is not installed

The system will automatically fall back to rule-based mode and continue working.

## Cost Estimation

Using `gpt-4o-mini`:
- ~100-200 tokens per query
- $0.15 per 1M input tokens, $0.60 per 1M output tokens
- **Estimated cost**: $0.0001-0.0003 per query (~$0.10-0.30 per 1000 queries)

For the 5 test scenarios in this notebook: **< $0.01**

## Security Note

⚠️ **Never commit your API key to version control!**

- Use environment variables
- Use `.env` files (add to `.gitignore`)
- In Colab, use Colab Secrets feature

## Support

If you encounter issues:
1. Check that your API key is correctly set
2. Verify you have credits in your OpenAI account
3. Try disabling LLM (`use_llm=False`) to test basic functionality
4. Check OpenAI status page: https://status.openai.com

## Next Steps

1. Run the database setup (Part 1 of notebook)
2. Set your API key (see Step 2 above)
3. Run test scenarios (Part 5 of notebook)
4. Try your own queries in interactive mode!
