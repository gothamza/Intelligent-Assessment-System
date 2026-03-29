#!/usr/bin/env python
"""
LangSmith Configuration Verification Script
Run this to verify your LangSmith setup is correct
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("=" * 60)
print("🔍 LangSmith Configuration Verification")
print("=" * 60)

# Check each required variable
required_vars = {
    "LANGSMITH_TRACING": os.getenv("LANGSMITH_TRACING"),
    "LANGSMITH_ENDPOINT": os.getenv("LANGSMITH_ENDPOINT"),
    "LANGSMITH_API_KEY": os.getenv("LANGSMITH_API_KEY"),
    "LANGSMITH_PROJECT": os.getenv("LANGSMITH_PROJECT")
}

all_set = True

for var_name, var_value in required_vars.items():
    if var_value:
        if var_name == "LANGSMITH_API_KEY":
            # Mask API key for security
            masked = var_value[:20] + "..." if len(var_value) > 20 else var_value
            print(f"✅ {var_name}: {masked}")
        else:
            print(f"✅ {var_name}: {var_value}")
    else:
        print(f"❌ {var_name}: NOT SET")
        all_set = False

print("=" * 60)

if not all_set:
    print("\n❌ CONFIGURATION INCOMPLETE")
    print("\nPlease ensure all LangSmith variables are set in your .env file:")
    print("  - LANGSMITH_TRACING=true")
    print("  - LANGSMITH_ENDPOINT=https://api.smith.langchain.com")
    print("  - LANGSMITH_API_KEY=lsv2_pt_your-key-here")
    print("  - LANGSMITH_PROJECT=your-project-name")
    print("\nThen restart your application.")
    exit(1)

# Verify tracing is enabled
if os.getenv("LANGSMITH_TRACING", "").lower() not in ["true", "1", "yes"]:
    print("\n⚠️  WARNING: LANGSMITH_TRACING is not set to 'true'")
    print(f"   Current value: {os.getenv('LANGSMITH_TRACING')}")
    print("\n   Tracing will be DISABLED!")
    print("   Set LANGSMITH_TRACING=true to enable tracing.")
else:
    print("\n✅ LangSmith tracing is ENABLED")

# Test API key format
api_key = os.getenv("LANGSMITH_API_KEY", "")
if not api_key.startswith("lsv2_pt_"):
    print("\n⚠️  WARNING: API key format may be incorrect")
    print(f"   Expected format: lsv2_pt_...")
    print(f"   Your key starts with: {api_key[:10]}...")

# Try to import LangChain
print("\n" + "=" * 60)
print("📦 Checking LangChain Installation")
print("=" * 60)

try:
    from langchain_groq import ChatGroq
    print("✅ langchain-groq installed")
except ImportError:
    print("❌ langchain-groq NOT installed")
    print("   Run: pip install langchain-groq")

try:
    from langchain.prompts import ChatPromptTemplate
    print("✅ langchain installed")
except ImportError:
    print("❌ langchain NOT installed")
    print("   Run: pip install langchain")

# Try to make a test LLM call
print("\n" + "=" * 60)
print("🧪 Testing LLM Call with LangSmith Tracing")
print("=" * 60)

try:
    from langchain_groq import ChatGroq
    
    # Get Groq API key
    groq_key = os.getenv("GROQ_API_KEY2") or os.getenv("GROQ_API_KEY")
    
    if not groq_key:
        print("❌ No Groq API key found")
        print("   Please set GROQ_API_KEY or GROQ_API_KEY2 in .env")
    else:
        print("✅ Groq API key found")
        print(f"   Making test call...")
        
        llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0.7,
            api_key=groq_key
        )
        
        response = llm.invoke("Say 'LangSmith test successful!' in French.")
        print(f"\n   LLM Response: {response.content}")
        print("\n✅ LLM call successful!")
        print("\n🔍 Check your LangSmith dashboard:")
        print(f"   https://smith.langchain.com/")
        print(f"   Project: {os.getenv('LANGSMITH_PROJECT')}")
        print("\n   You should see a new trace for this test call!")
        
except Exception as e:
    print(f"\n❌ Error during LLM test: {e}")
    print("\n   This might be a network issue or invalid API key.")

print("\n" + "=" * 60)
print("✅ Verification Complete!")
print("=" * 60)
print("\nNext steps:")
print("1. If all checks passed, run your Streamlit app")
print("2. Use the application and generate some questions")
print("3. Check LangSmith dashboard for traces")
print(f"\nLangSmith Dashboard: https://smith.langchain.com/")
print("=" * 60)

