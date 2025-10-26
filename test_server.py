import requests
import time

def test_server():
    """Test if the OpenManus server is running correctly"""
    try:
        # Test health endpoint
        print("Testing health endpoint...")
        response = requests.get("http://localhost:5000/api/health", timeout=10)
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"Response: {response.json()}")
        else:
            print(f"❌ Health check failed with status code: {response.status_code}")
            return False
            
        # Test initialization endpoint
        print("\nTesting initialization endpoint...")
        response = requests.get("http://localhost:5000/api/init", timeout=10)
        if response.status_code == 200:
            print("✅ Initialization endpoint passed")
            print(f"Response: {response.json()}")
        else:
            print(f"❌ Initialization endpoint failed with status code: {response.status_code}")
            return False
            
        # Test chat endpoint with a simple message
        print("\nTesting chat endpoint...")
        chat_data = {"message": "Hello, how are you?"}
        response = requests.post("http://localhost:5000/api/chat", json=chat_data, timeout=30)
        if response.status_code == 200:
            result = response.json()
            print("✅ Chat endpoint passed")
            print(f"Response: {result}")
            
            # If it's queued, check the result
            if result.get("queued"):
                query_id = result.get("query_id")
                print(f"Message queued with ID: {query_id}")
                print("Checking query result...")
                
                # Wait a moment and check the result
                time.sleep(5)
                result_response = requests.get(f"http://localhost:5000/api/query/{query_id}", timeout=10)
                if result_response.status_code == 200:
                    print(f"Query result: {result_response.json()}")
                else:
                    print(f"Failed to get query result: {result_response.status_code}")
        else:
            print(f"❌ Chat endpoint failed with status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
        print("\n🎉 All tests passed! The OpenManus server is running correctly.")
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the server. Make sure it's running on http://localhost:5000")
        return False
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        return False

if __name__ == "__main__":
    test_server()