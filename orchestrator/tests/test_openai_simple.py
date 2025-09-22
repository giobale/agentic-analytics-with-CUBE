# ABOUTME: Simple OpenAI API test to isolate connection and authentication issues
# ABOUTME: Minimal test to debug LLM processing failures in the orchestrator

import os
import sys
from pathlib import Path

# Load environment variables
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent.parent / '.env'
    load_dotenv(env_path)
    print(f"✅ Loaded .env from: {env_path}")
except ImportError:
    print("⚠️  python-dotenv not installed, using system env vars only")

try:
    import openai
    print("✅ OpenAI package imported successfully")
except ImportError:
    print("❌ OpenAI package not installed. Run: pip install openai")
    sys.exit(1)


def test_api_key():
    """Test if API key is properly configured."""
    print("\n🔑 Testing API Key Configuration...")

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        print("❌ OPENAI_API_KEY not found in environment")
        return False

    if not api_key.startswith("sk-"):
        print(f"❌ Invalid API key format: {api_key[:10]}...")
        return False

    print(f"✅ API Key found: {api_key[:20]}...{api_key[-10:]}")
    return True


def test_basic_connection():
    """Test basic OpenAI API connectivity."""
    print("\n🌐 Testing Basic API Connection...")

    try:
        client = openai.OpenAI()

        # Simple test call
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Use cheaper model for testing
            messages=[{"role": "user", "content": "Say 'Hello World'"}],
            max_tokens=10
        )

        print("✅ Basic API connection successful")
        print(f"   Response: {response.choices[0].message.content}")
        print(f"   Usage: {response.usage.total_tokens} tokens")
        return True

    except openai.AuthenticationError as e:
        print(f"❌ Authentication failed: {str(e)}")
        return False
    except openai.RateLimitError as e:
        print(f"❌ Rate limit exceeded: {str(e)}")
        return False
    except openai.APIConnectionError as e:
        print(f"❌ API connection error: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False


def test_gpt4_access():
    """Test if GPT-4 model is accessible."""
    print("\n🧠 Testing GPT-4 Model Access...")

    try:
        client = openai.OpenAI()

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": "Say 'GPT-4 works'"}],
            max_tokens=10
        )

        print("✅ GPT-4 access successful")
        print(f"   Response: {response.choices[0].message.content}")
        print(f"   Usage: {response.usage.total_tokens} tokens")
        return True

    except openai.AuthenticationError as e:
        print(f"❌ GPT-4 authentication failed: {str(e)}")
        return False
    except openai.NotFoundError as e:
        print(f"❌ GPT-4 model not found/accessible: {str(e)}")
        print("💡 Try upgrading your OpenAI account or use gpt-3.5-turbo")
        return False
    except Exception as e:
        print(f"❌ GPT-4 access error: {str(e)}")
        return False


def test_json_response():
    """Test JSON response format (required by orchestrator)."""
    print("\n📋 Testing JSON Response Format...")

    try:
        client = openai.OpenAI()

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant. Always respond with ONLY valid JSON."},
                {"role": "user", "content": "Return a JSON object with 'status': 'success' and 'message': 'JSON works'"}
            ],
            max_tokens=50
        )

        import json
        content = response.choices[0].message.content
        parsed_json = json.loads(content)

        print("✅ JSON response format successful")
        print(f"   Raw response: {content}")
        print(f"   Parsed JSON: {parsed_json}")
        return True

    except json.JSONDecodeError as e:
        print(f"❌ JSON parsing failed: {str(e)}")
        print(f"   Raw response: {response.choices[0].message.content}")
        return False
    except Exception as e:
        print(f"❌ JSON response test failed: {str(e)}")
        return False


def test_orchestrator_like_request():
    """Test a request similar to what the orchestrator sends."""
    print("\n🎯 Testing Orchestrator-like Request...")

    try:
        client = openai.OpenAI()

        # Simulate orchestrator request
        system_prompt = """You are an expert data analyst. Convert natural language to CUBE API queries.

        Always respond with valid JSON in this format:
        {
          "response_type": "cube_query",
          "cube_query": {
            "measures": ["ViewName.measure_name"],
            "dimensions": ["ViewName.dimension_name"]
          },
          "interpretation": "Brief explanation",
          "confidence_score": 0.95
        }"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": "Show me total revenue by event"}
        ]

        response = client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            temperature=0.1,
            max_tokens=500
        )

        import json
        content = response.choices[0].message.content
        parsed_json = json.loads(content)

        print("✅ Orchestrator-like request successful")
        print(f"   Response type: {parsed_json.get('response_type')}")
        print(f"   Has cube_query: {'cube_query' in parsed_json}")
        print(f"   Usage: {response.usage.total_tokens} tokens")
        return True

    except Exception as e:
        print(f"❌ Orchestrator-like request failed: {str(e)}")
        return False


def main():
    """Run all OpenAI API tests."""
    print("🚀 OPENAI API DIAGNOSTIC TEST")
    print("=" * 40)

    tests = [
        ("API Key Configuration", test_api_key),
        ("Basic Connection", test_basic_connection),
        ("GPT-4 Access", test_gpt4_access),
        ("JSON Response Format", test_json_response),
        ("Orchestrator-like Request", test_orchestrator_like_request)
    ]

    results = {}

    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except KeyboardInterrupt:
            print(f"\n❌ Test interrupted by user")
            break
        except Exception as e:
            print(f"\n❌ Test '{test_name}' crashed: {str(e)}")
            results[test_name] = False

    # Summary
    print(f"\n📊 TEST SUMMARY")
    print("-" * 25)

    passed = 0
    total = len(results)

    for test_name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if success:
            passed += 1

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! OpenAI integration should work.")
    else:
        print("⚠️  Some tests failed. Check the errors above.")

        # Specific recommendations
        if not results.get("API Key Configuration"):
            print("💡 Fix: Check your OPENAI_API_KEY in the .env file")
        elif not results.get("Basic Connection"):
            print("💡 Fix: Check internet connection and OpenAI service status")
        elif not results.get("GPT-4 Access"):
            print("💡 Fix: Upgrade OpenAI account or change model to gpt-3.5-turbo")

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)