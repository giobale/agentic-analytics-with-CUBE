#!/usr/bin/env python3
"""
Test script to validate OpenAI Structured Outputs schema.
This replicates the exact API call made by the orchestrator.
"""

import os
import json
from openai import OpenAI
from response_models import get_response_schema

def test_openai_structured_outputs():
    """Test the OpenAI API call with Structured Outputs"""

    # Get API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ Error: OPENAI_API_KEY environment variable not set")
        return

    # Initialize client
    client = OpenAI(api_key=api_key)

    # Get the schema
    response_schema = get_response_schema()

    print("=" * 80)
    print("🔍 Testing OpenAI JSON Mode")
    print("=" * 80)
    print(f"\n📋 Using: json_object mode (simpler than json_schema)")
    print(f"📋 This guarantees JSON output without strict schema validation")
    print("\n" + "=" * 80)

    # Prepare test messages
    system_prompt = """You are a data analyst assistant that converts natural language questions into CUBE API queries.

IMPORTANT: You MUST always respond with valid JSON format. Never return plain text.
Always use JSON format for all responses in one of these formats:

1. For CUBE queries:
{
  "response_type": "cube_query",
  "cube_query": { ... },
  "description": "...",
  "confidence_score": 0.9
}

2. For clarifications:
{
  "response_type": "clarification_needed",
  "message": "...",
  "questions": ["...", "..."],
  "suggestions": ["...", "..."],
  "confidence_score": 0.7
}

3. For errors:
{
  "response_type": "error",
  "description": "...",
  "confidence_score": 0.0
}
"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": "Can you tell me the daily tickets sold?"}
    ]

    print("\n🚀 Making OpenAI API Call...")
    print(f"   Model: gpt-4o")
    print(f"   Messages: {len(messages)}")
    print(f"   Using JSON Mode: Yes\n")

    try:
        # Make the API call exactly as the orchestrator does
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.1,
            max_tokens=2000,
            response_format={"type": "json_object"}
        )

        print("✅ API call successful!\n")
        print("=" * 80)
        print("📨 Response:")
        print("=" * 80)

        response_content = response.choices[0].message.content
        parsed = json.loads(response_content)

        print(json.dumps(parsed, indent=2))
        print("\n" + "=" * 80)
        print(f"✅ Response Type: {parsed.get('response_type')}")
        print(f"✅ Confidence Score: {parsed.get('confidence_score')}")
        print(f"✅ Tokens Used: {response.usage.total_tokens} ({response.usage.prompt_tokens} prompt + {response.usage.completion_tokens} completion)")
        print("=" * 80)

    except Exception as e:
        print(f"\n❌ Error occurred:\n")
        print(f"   Error Type: {type(e).__name__}")
        print(f"   Error Message: {str(e)}")
        print("\n" + "=" * 80)

        # If it's a BadRequestError, show more details
        if hasattr(e, 'response'):
            try:
                error_data = e.response.json()
                print("\n📋 Error Details:")
                print(json.dumps(error_data, indent=2))
            except:
                pass

if __name__ == "__main__":
    test_openai_structured_outputs()
