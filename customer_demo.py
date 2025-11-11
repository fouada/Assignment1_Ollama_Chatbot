#!/usr/bin/env python3
"""
Customer Model Flexibility Demo
Demonstrates how easy it is for customers to use different models
"""

import requests
import time
from typing import List, Dict
import json


class ModelFlexibilityDemo:
    """Demo showing model customization capabilities"""

    def __init__(self, api_url: str = "http://localhost:5001"):
        self.api_url = api_url

    def test_connection(self) -> bool:
        """Test if API is accessible"""
        try:
            response = requests.get(f"{self.api_url}/health", timeout=5)
            return response.status_code == 200
        except Exception as e:
            print(f"❌ Cannot connect to API at {self.api_url}")
            print(f"   Error: {e}")
            print(f"\n💡 Make sure the Flask app is running:")
            print(f"   python apps/app_flask.py")
            return False

    def list_models(self) -> List[Dict]:
        """Fetch available models from API"""
        try:
            print("📋 Fetching available models...")
            response = requests.get(f"{self.api_url}/models")
            data = response.json()

            print(f"✅ Found {data['count']} models:\n")

            models = data["models"]
            for model in models:
                name = model["name"]
                size_gb = model["size"] / (1024**3)
                params = model["details"].get("parameter_size", "Unknown")
                family = model["details"].get("family", "Unknown")

                print(f"   🤖 {name}")
                print(f"      Size: {size_gb:.2f} GB")
                print(f"      Parameters: {params}")
                print(f"      Family: {family}")
                print()

            return models

        except Exception as e:
            print(f"❌ Error fetching models: {e}")
            return []

    def test_model(self, model_name: str, prompt: str) -> Dict:
        """Test a single model with a prompt"""
        try:
            start_time = time.time()

            response = requests.post(
                f"{self.api_url}/chat",
                json={
                    "message": prompt,
                    "model": model_name,
                    "temperature": 0.7,
                    "stream": False
                },
                timeout=60
            )

            duration = time.time() - start_time

            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "response": result.get("response", ""),
                    "duration": duration,
                    "model": model_name
                }
            else:
                return {
                    "success": False,
                    "error": response.text,
                    "duration": duration,
                    "model": model_name
                }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "duration": 0,
                "model": model_name
            }

    def compare_models(self, models: List[str], prompt: str):
        """Compare multiple models with the same prompt"""
        print("="*70)
        print("MODEL COMPARISON TEST")
        print("="*70)
        print(f"\n📝 Prompt: \"{prompt}\"\n")

        results = []

        for model_name in models:
            print(f"🔄 Testing model: {model_name}...")

            result = self.test_model(model_name, prompt)

            if result["success"]:
                response_text = result["response"]
                duration = result["duration"]

                print(f"✅ Response received ({duration:.2f}s)")
                print(f"   Length: {len(response_text)} characters")
                print(f"   Preview: {response_text[:100]}...")
                print()

                results.append(result)
            else:
                print(f"❌ Error: {result['error']}")
                print()

            time.sleep(1)  # Brief pause between requests

        return results

    def show_api_examples(self):
        """Show example API calls for different models"""
        print("="*70)
        print("API USAGE EXAMPLES")
        print("="*70)
        print("\n1️⃣  Basic Chat (Python requests):\n")

        print("```python")
        print("import requests")
        print()
        print("response = requests.post(")
        print("    'http://your-api.com/chat',")
        print("    json={")
        print("        'message': 'Hello, world!',")
        print("        'model': 'mistral',  # Change this to any model!")
        print("        'temperature': 0.7")
        print("    }")
        print(")")
        print("print(response.json()['response'])")
        print("```\n")

        print("2️⃣  Using cURL:\n")
        print("```bash")
        print("curl -X POST http://your-api.com/chat \\")
        print("  -H 'Content-Type: application/json' \\")
        print("  -d '{")
        print('    "message": "Explain AI",')
        print('    "model": "llama3.2"')
        print("  }'")
        print("```\n")

        print("3️⃣  List Available Models:\n")
        print("```bash")
        print("curl http://your-api.com/models")
        print("```\n")

        print("4️⃣  Streaming Responses:\n")
        print("```python")
        print("response = requests.post(")
        print("    'http://your-api.com/chat',")
        print("    json={'message': 'Tell a story', 'model': 'phi3', 'stream': True},")
        print("    stream=True")
        print(")")
        print()
        print("for line in response.iter_lines():")
        print("    if line:")
        print("        print(line.decode('utf-8'))")
        print("```\n")

    def demonstrate_use_cases(self):
        """Show different use cases for model selection"""
        print("="*70)
        print("USE CASE EXAMPLES")
        print("="*70)
        print()

        use_cases = [
            {
                "scenario": "Quick FAQ / Simple Queries",
                "recommended_model": "phi3",
                "reason": "Fastest response time, lowest resource usage",
                "example": "What is 2+2?"
            },
            {
                "scenario": "General Conversation",
                "recommended_model": "llama3.2:8b",
                "reason": "Balanced quality and performance",
                "example": "Tell me about renewable energy"
            },
            {
                "scenario": "Code Generation / Review",
                "recommended_model": "codellama",
                "reason": "Specialized for programming tasks",
                "example": "Write a Python function to sort a list"
            },
            {
                "scenario": "Complex Analysis / Research",
                "recommended_model": "llama3.1:70b",
                "reason": "Highest quality reasoning",
                "example": "Analyze the economic impact of AI"
            },
            {
                "scenario": "Creative Writing",
                "recommended_model": "mistral",
                "reason": "Excellent at creative tasks",
                "example": "Write a short poem about nature"
            }
        ]

        for i, use_case in enumerate(use_cases, 1):
            print(f"{i}. {use_case['scenario']}")
            print(f"   📌 Recommended: {use_case['recommended_model']}")
            print(f"   💡 Reason: {use_case['reason']}")
            print(f"   📝 Example: \"{use_case['example']}\"")
            print()

    def show_customization_options(self):
        """Show how customers can customize"""
        print("="*70)
        print("CUSTOMIZATION OPTIONS FOR CUSTOMERS")
        print("="*70)
        print()

        print("1️⃣  Via Configuration File (Simplest):\n")
        print("   Edit: plugins/config.yaml")
        print("   ```yaml")
        print("   backends:")
        print("     ollama:")
        print("       config:")
        print("         default_model: 'mistral'  # Change default")
        print("   ```\n")

        print("2️⃣  Via UI (User-Friendly):\n")
        print("   • Open Streamlit interface")
        print("   • Select model from dropdown")
        print("   • Adjust temperature slider")
        print("   • Changes apply immediately\n")

        print("3️⃣  Via API (Programmatic):\n")
        print("   • Specify 'model' parameter in each request")
        print("   • Different users can use different models")
        print("   • Full flexibility, zero configuration\n")

        print("4️⃣  Add New Models (2 Minutes):\n")
        print("   ```bash")
        print("   # Browse available models")
        print("   ollama list")
        print()
        print("   # Pull new model")
        print("   ollama pull gemma:7b")
        print()
        print("   # Use immediately (no restart needed!)")
        print("   # Model appears in UI dropdown automatically")
        print("   ```\n")

        print("5️⃣  Advanced: Model Routing:\n")
        print("   • Route by customer tier (free/premium/enterprise)")
        print("   • Route by task complexity")
        print("   • Route by department")
        print("   • Route by region\n")


def main():
    """Run the complete demo"""
    print("\n" + "="*70)
    print("🚀 CUSTOMER MODEL FLEXIBILITY DEMONSTRATION")
    print("="*70)
    print()

    demo = ModelFlexibilityDemo()

    # Test connection
    print("🔌 Testing API connection...")
    if not demo.test_connection():
        return

    print("✅ API is accessible!\n")

    # List available models
    models = demo.list_models()

    if not models:
        print("\n⚠️  No models found. Install some models first:")
        print("   ollama pull llama3.2")
        print("   ollama pull mistral")
        print("   ollama pull phi3")
        return

    # Show API examples
    demo.show_api_examples()

    # Show use cases
    demo.demonstrate_use_cases()

    # Show customization options
    demo.show_customization_options()

    # Compare models (if multiple available)
    if len(models) >= 2:
        print("="*70)
        print("LIVE MODEL COMPARISON")
        print("="*70)
        print()

        # Use first 2-3 models for comparison
        test_models = [m["name"] for m in models[:min(3, len(models))]]
        test_prompt = "What is machine learning?"

        print(f"📊 Comparing {len(test_models)} models with same prompt:\n")

        results = demo.compare_models(test_models, test_prompt)

        if results:
            print("="*70)
            print("COMPARISON SUMMARY")
            print("="*70)
            print()

            # Sort by response time
            results_sorted = sorted(results, key=lambda x: x["duration"])

            print("🏆 Performance Ranking (by speed):\n")
            for i, result in enumerate(results_sorted, 1):
                print(f"   {i}. {result['model']}: {result['duration']:.2f}s")

            print()
            print("💡 Key Insight:")
            print("   Different models have different speeds and capabilities.")
            print("   Your customers can choose based on their needs!")

    print("\n" + "="*70)
    print("✅ DEMO COMPLETE!")
    print("="*70)
    print()
    print("📚 Key Takeaways:")
    print("   • Switching models is as easy as changing a parameter")
    print("   • No code changes required")
    print("   • Works via UI and API")
    print("   • Add new models in seconds")
    print("   • Each customer can use their preferred model")
    print()
    print("📖 For more details, see: CUSTOMER_MODEL_CUSTOMIZATION_GUIDE.md")
    print()


if __name__ == "__main__":
    main()
