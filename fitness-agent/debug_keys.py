"""Debug API key loading issues"""
import os
from dotenv import load_dotenv
from pathlib import Path

print("=== API Key Debug ===\n")

# 1. Force load .env with override
dotenv_path = Path(__file__).resolve().parent / ".env"
print(f"Loading .env from: {dotenv_path}")
print(f".env exists: {dotenv_path.exists()}")

if dotenv_path.exists():
    load_dotenv(dotenv_path=dotenv_path, override=True)
    print("✅ .env loaded with override=True\n")
else:
    print("❌ .env file not found!\n")

# 2. Check environment variables (both shell and loaded)
print("=== Environment Variable Check ===")
for name in ["ANTHROPIC_API_KEY", "OPENAI_API_KEY", "GEMINI_API_KEY"]:
    v = os.getenv(name)
    print(f"{name}:")
    print(f"  exists: {bool(v)}")
    if v:
        print(f"  repr: {repr(v[:15])}...{repr(v[-8:])}")  # Show quotes/spaces without full key
        print(f"  length: {len(v)}")
        print(f"  stripped: {v == v.strip()}")
        has_quotes = v.startswith(('"', "'")) or v.endswith(('"', "'"))
        print(f"  has_quotes: {has_quotes}")
    print()

# 3. Check for shell environment variables that might override
print("=== Shell Environment Check ===")
print("Checking if keys exist in shell environment...")
for name in ["ANTHROPIC_API_KEY", "OPENAI_API_KEY", "GEMINI_API_KEY"]:
    # This will show if the key exists in the shell environment
    shell_var = os.environ.get(name)
    if shell_var:
        print(f"⚠️  {name} found in shell environment")
    else:
        print(f"✅ {name} not in shell environment")