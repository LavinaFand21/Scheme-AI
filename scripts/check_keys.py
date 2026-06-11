import os
import sys

# Ensure backend package is on path to load the .env variables
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    import backend
except ImportError:
    pass

gemini_key = os.environ.get("GEMINI_API_KEY")
groq_key = os.environ.get("GROQ_API_KEY")

print("=========================================")
print("          Scheme-AI Key Checker          ")
print("=========================================")

if gemini_key:
    # Safely show prefix
    prefix = gemini_key[:7] if len(gemini_key) > 7 else gemini_key
    print(f"✅ GEMINI_API_KEY is set in environment (starts with: '{prefix}...')")
else:
    print("❌ GEMINI_API_KEY is NOT set in environment.")
    
if groq_key:
    prefix = groq_key[:7] if len(groq_key) > 7 else groq_key
    print(f"✅ GROQ_API_KEY is set in environment (starts with: '{prefix}...')")
else:
    print("❌ GROQ_API_KEY is NOT set in environment.")

print("-----------------------------------------")
if gemini_key:
    print("🚀 Status: Active LLM Engine -> GOOGLE GEMINI")
elif groq_key:
    print("🚀 Status: Active LLM Engine -> META LLAMA-3 (via Groq)")
else:
    print("⚠️ Status: Active LLM Engine -> LOCAL DEMO MODE (Local logic fallback)")
print("=========================================")
