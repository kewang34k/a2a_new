# 🔑 API Key Setup Guide for LLM-Enhanced Multi-Agent System

## Quick Answer: Where to Put Your API Key

### For Jupyter Notebooks (Google Colab, Jupyter Lab, etc.):

```python
# Add this at the TOP of your notebook, before running any cells
import os
os.environ['OPENAI_API_KEY'] = 'sk-your-actual-api-key-here'
```

That's it! Replace `'sk-your-actual-api-key-here'` with your real API key.

---

## Step-by-Step Setup

### Step 1: Get Your OpenAI API Key

1. **Go to OpenAI**: [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)

2. **Sign up or log in** to your OpenAI account

3. **Create a new key**:
   - Click "+ Create new secret key"
   - Give it a name (e.g., "Multi-Agent System")
   - Copy the key (starts with `sk-`)
   - **IMPORTANT**: Save it somewhere safe - you can't see it again!

4. **Add credits** (if needed):
   - Go to Settings → Billing
   - Add at least $5 credit
   - Set up usage limits to avoid surprises

### Step 2: Choose Your Setup Method

## Method 1: Google Colab (Recommended for Notebooks)

```python
# Cell 1: Set API Key
import os
os.environ['OPENAI_API_KEY'] = 'sk-proj-abc123...'  # Your actual key

# Verify it's set
if os.getenv('OPENAI_API_KEY', '').startswith('sk-'):
    print("✓ API Key is configured!")
else:
    print("❌ API Key not found")
```

**OR use Colab Secrets (more secure):**

```python
# 1. Click the key icon (🔑) in left sidebar
# 2. Add secret: Name="OPENAI_API_KEY", Value="sk-your-key"
# 3. Enable notebook access

from google.colab import userdata
os.environ['OPENAI_API_KEY'] = userdata.get('OPENAI_API_KEY')
```

## Method 2: Local Python Script / Jupyter

### Option A: Environment Variable (Recommended)

**Linux/Mac:**
```bash
# In terminal, before running Python
export OPENAI_API_KEY='sk-your-key-here'
python demo_llm.py
```

**Windows:**
```cmd
REM In command prompt
set OPENAI_API_KEY=sk-your-key-here
python demo_llm.py
```

### Option B: .env File (Best for Development)

1. Create a file named `.env` in the project folder:
```bash
# .env
OPENAI_API_KEY=sk-your-actual-key-here
OPENAI_MODEL=gpt-4o-mini
```

2. The system automatically loads it:
```python
# No code needed! config.py loads .env automatically
from config import get_config
config = get_config()
# API key is already set
```

### Option C: Set in Code (Quick Testing)

```python
from config import get_config

config = get_config()
config.set_api_key('sk-your-key-here')
```

## Method 3: Direct in Notebook Cells

In your Jupyter/Colab notebook:

```python
# === CONFIGURATION CELL (Run this first!) ===
import os

# Set your API key
os.environ['OPENAI_API_KEY'] = 'sk-proj-abc123...'  # ← Put your key here

# Optional: Choose model
os.environ['OPENAI_MODEL'] = 'gpt-4o-mini'  # Cheapest option

print("✓ Configuration set!")
```

---

## Verification

After setting your key, verify it works:

```python
from config import get_config

config = get_config()

if config.validate():
    print("✓ API key is valid and ready to use!")
    print(f"  Model: {config.openai_model}")
else:
    print("❌ API key not configured")
    print("  Set OPENAI_API_KEY environment variable")
```

---

## Using the System

### With LLM (API Key Required):

```python
from a2a_system_llm import A2ACoordinationSystemLLM

# Initialize with LLM enabled
system = A2ACoordinationSystemLLM("support.db", use_llm=True)

# Process query
result = system.process_query("I need help with my account")
print(result['response'])
```

### Without LLM (No API Key):

```python
from a2a_system_llm import A2ACoordinationSystemLLM

# Initialize with LLM disabled (fallback to rules)
system = A2ACoordinationSystemLLM("support.db", use_llm=False)

# Works the same way
result = system.process_query("Get customer information for ID 5")
print(result['response'])
```

The system **automatically falls back** to rule-based mode if:
- No API key is set
- API key is invalid
- OpenAI package is not installed

---

## Security Best Practices

### ✅ DO:
- Use environment variables
- Use `.env` files (and add to `.gitignore`)
- Use Colab Secrets in Colab notebooks
- Keep API keys private
- Set usage limits in OpenAI dashboard

### ❌ DON'T:
- Hardcode keys in files you commit to Git
- Share your API key publicly
- Use your key in client-side code
- Forget to add `.env` to `.gitignore`

### Add to .gitignore:
```
.env
*.env
.env.local
```

---

## Model Selection

| Model | Speed | Quality | Cost/1M tokens | Use Case |
|-------|-------|---------|----------------|----------|
| `gpt-4o-mini` | ⚡⚡⚡ | ⭐⭐⭐ | $0.15 input, $0.60 output | **Recommended** for this project |
| `gpt-4o` | ⚡⚡ | ⭐⭐⭐⭐⭐ | $2.50 input, $10.00 output | Best quality |
| `gpt-4-turbo` | ⚡ | ⭐⭐⭐⭐ | $10.00 input, $30.00 output | Legacy |

**For this assignment: Use `gpt-4o-mini`** - it's 90% as good at 5% the cost.

Set it:
```python
os.environ['OPENAI_MODEL'] = 'gpt-4o-mini'
```

---

## Cost Estimation

### For This Project:

- **5 test scenarios**: ~$0.001 (less than a penny)
- **100 queries**: ~$0.01
- **1000 queries**: ~$0.10

Each query uses approximately:
- 150 input tokens (query + context)
- 100 output tokens (response)
- Total: ~250 tokens = **$0.0001 per query**

### Monthly Estimates:

| Usage | Queries/Day | Monthly Cost |
|-------|-------------|--------------|
| Development | 50 | $0.15 |
| Testing | 200 | $0.60 |
| Production | 1000 | $3.00 |

**Note**: These are estimates with `gpt-4o-mini`. Actual costs may vary.

---

## Troubleshooting

### Issue: "OpenAI API key not configured"

**Solution**:
```python
import os
print("Current key:", os.getenv('OPENAI_API_KEY', 'NOT SET'))

# If NOT SET, add it:
os.environ['OPENAI_API_KEY'] = 'sk-your-key-here'
```

### Issue: "Module 'openai' not found"

**Solution**:
```bash
pip install openai>=1.0.0
```

Or in Colab:
```python
!pip install -q openai>=1.0.0
```

### Issue: "API key invalid"

**Possible causes**:
1. Typo in the key
2. Key was revoked
3. No credits in OpenAI account

**Solution**:
1. Generate a new key at platform.openai.com
2. Add billing credits
3. Check usage limits

### Issue: System uses rule-based mode even with key set

**Debug**:
```python
from config import get_config

config = get_config()
print("API key present:", bool(config.openai_api_key))
print("Valid config:", config.validate())

# Try getting client
try:
    client = config.get_openai_client()
    print("✓ OpenAI client created successfully!")
except Exception as e:
    print(f"❌ Error: {e}")
```

---

## Example: Complete Setup

```python
# === Complete Notebook Setup ===

# 1. Install dependencies (run once)
!pip install -q openai python-dotenv

# 2. Set API key
import os
os.environ['OPENAI_API_KEY'] = 'sk-proj-abc123...'  # ← YOUR KEY HERE
os.environ['OPENAI_MODEL'] = 'gpt-4o-mini'

# 3. Verify
from config import get_config
config = get_config()
assert config.validate(), "API key not set correctly!"
print("✓ Ready to use LLM features!")

# 4. Initialize system
from a2a_system_llm import A2ACoordinationSystemLLM
system = A2ACoordinationSystemLLM("support.db", use_llm=True)

# 5. Test it
result = system.process_query("Help me upgrade my account")
print(result['response'])
```

---

## Need Help?

1. **Check setup_instructions.md** - Full setup guide
2. **Run demo_llm.py** - Interactive demo with prompts
3. **Use `use_llm=False`** - Test without API key first
4. **Check OpenAI status** - status.openai.com

---

## Summary: 3 Ways to Set API Key

### Quick (for testing):
```python
import os
os.environ['OPENAI_API_KEY'] = 'sk-...'
```

### Secure (for Colab):
```python
from google.colab import userdata
os.environ['OPENAI_API_KEY'] = userdata.get('OPENAI_API_KEY')
```

### Professional (for development):
```bash
# Create .env file
echo "OPENAI_API_KEY=sk-..." > .env
# It loads automatically
```

**Choose the method that works for your environment!**
