"""Quick test script to verify API keys work"""
import os
from dotenv import load_dotenv

load_dotenv()

print("=== API Key Test ===\n")

# Test Anthropic
print("1. Testing Anthropic (Claude)...")
anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
if not anthropic_key:
    print("   ❌ ANTHROPIC_API_KEY not set")
else:
    print(f"   Key found: {anthropic_key[:20]}...{anthropic_key[-10:]}")
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=anthropic_key)
        response = client.messages.create(
            model="claude-sonnet-4-20250514",  # Using a lighter model for test
            max_tokens=50,
            messages=[{"role": "user", "content": "Say 'API key works!' in 3 words"}]
        )
        print(f"   ✅ SUCCESS: {response.content[0].text}")
    except Exception as e:
        print(f"   ❌ FAILED: {e}")

print()

# Test OpenAI
print("2. Testing OpenAI (GPT)...")
openai_key = os.environ.get("OPENAI_API_KEY")
if not openai_key:
    print("   ❌ OPENAI_API_KEY not set")
else:
    print(f"   Key found: {openai_key[:20]}...{openai_key[-10:]}")
    try:
        import openai
        client = openai.OpenAI(api_key=openai_key)
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Using a lighter model for test
            max_tokens=50,
            messages=[{"role": "user", "content": "Say 'API key works!' in 3 words"}]
        )
        print(f"   ✅ SUCCESS: {response.choices[0].message.content}")
    except Exception as e:
        print(f"   ❌ FAILED: {e}")

print()

# Test Gemini
print("3. Testing Gemini...")
gemini_key = os.environ.get("GEMINI_API_KEY")
if not gemini_key:
    print("   ⏭️  GEMINI_API_KEY not set (optional)")
else:
    print(f"   Key found: {gemini_key[:10]}...{gemini_key[-5:]}")
    try:
        import google.generativeai as genai
        genai.configure(api_key=gemini_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content("Say 'API key works!' in 3 words")
        print(f"   ✅ SUCCESS: {response.text}")
    except Exception as e:
        print(f"   ❌ FAILED: {e}")

print("\n=== Test Complete ===")



