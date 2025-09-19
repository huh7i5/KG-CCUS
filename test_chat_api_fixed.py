#!/usr/bin/env python3
"""
Test the chat API to verify it works after the sents field fix
"""

import requests
import json
import time

def test_chat_api():
    """Test the chat API with CCUS-related queries"""

    url = "http://127.0.0.1:8000/chat/"

    test_queries = [
        "什么是CCUS技术？",
        "二氧化碳储存有哪些方法？",
        "鄂尔多斯示范工程是什么？",
        "碳捕集技术的应用前景如何？"
    ]

    print("🚀 Testing Chat API...")
    print(f"API URL: {url}")

    for i, query in enumerate(test_queries, 1):
        print(f"\n📝 Test {i}: {query}")

        try:
            # Prepare the request
            payload = {
                "query": query,
                "stream": False  # Use non-streaming for easier testing
            }

            # Send the request
            response = requests.post(url, json=payload, timeout=30)

            if response.status_code == 200:
                try:
                    result = response.json()
                    print(f"  ✅ Status: {response.status_code}")
                    print(f"  📊 Response: {result.get('response', 'No response field')[:200]}...")

                    # Check if knowledge graph was used
                    entities = result.get('entities', [])
                    graph_info = result.get('graph_info', {})

                    if entities:
                        print(f"  🔍 Entities found: {entities}")
                    if graph_info:
                        print(f"  📈 Graph info: {graph_info}")

                except json.JSONDecodeError:
                    print(f"  ⚠️  Response is not JSON: {response.text[:200]}...")

            else:
                print(f"  ❌ HTTP Error: {response.status_code}")
                print(f"  📄 Response: {response.text[:200]}...")

        except requests.exceptions.ConnectionError:
            print(f"  ❌ Connection Error: Could not connect to {url}")
            print("  💡 Make sure the server is running: python start_system.py")
            break

        except requests.exceptions.Timeout:
            print(f"  ⏰ Timeout: Request took longer than 30 seconds")

        except Exception as e:
            print(f"  ❌ Unexpected error: {e}")

        # Wait a bit between requests
        time.sleep(1)

    print("\n🏁 Chat API testing completed!")

if __name__ == "__main__":
    test_chat_api()