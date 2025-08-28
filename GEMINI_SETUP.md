# Google Gemini API Setup Guide

## 🚀 How to Get Your Google Gemini API Key

### Step 1: Go to Google AI Studio
Visit: https://aistudio.google.com/app/apikey

### Step 2: Sign in with Google Account
- Use your Google account to sign in
- Accept the terms of service

### Step 3: Create API Key
1. Click **"Create API Key"**
2. Choose **"Create API key in new project"** (recommended)
3. Copy the generated API key

### Step 4: Add to Your Project
Edit the `.env` file in your project:
```bash
GOOGLE_API_KEY=your_actual_api_key_here
```

## 💰 Pricing Information

### Free Tier (Generous!)
- **15 requests per minute**
- **1 million tokens per day**
- **1,500 requests per day**

### Paid Tier
- **Gemini 1.5 Flash**: $0.075 per 1M input tokens
- **Gemini 1.5 Pro**: $1.25 per 1M input tokens

## 🔧 Models Available

### Gemini 1.5 Flash (Default)
- Fast responses
- Good for most use cases
- Cost-effective

### Gemini 1.5 Pro
- Higher quality responses
- Better reasoning
- More expensive

## ✅ Benefits Over OpenAI

1. **Generous Free Tier**: 1M tokens/day vs OpenAI's limited free credits
2. **Lower Cost**: Significantly cheaper than GPT models
3. **Large Context**: Up to 1M tokens context window
4. **No Quota Issues**: More reliable access
5. **Good Performance**: Comparable quality to GPT-3.5/4

## 🛠️ Configuration

The system is already configured to use:
- **Model**: `gemini-1.5-flash`
- **Temperature**: 0.7
- **Max Tokens**: 2048

You can modify these in `utils/config.py` if needed.

## 🧪 Testing

After adding your API key, test with:
```bash
python3 -c "
import sys
sys.path.append('src')
from chat_gemini import GeminiChatInterface
chat = GeminiChatInterface()
print('Gemini setup successful!')
"
```
