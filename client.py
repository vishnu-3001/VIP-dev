import requests

def get_openai_response():
    # Send a GET request to the modified /collaboration/invoke endpoint
    response = requests.get("http://localhost:8000/collaboration/invoke")
    
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": "Failed to get response", "status_code": response.status_code, "detail": response.text}

if __name__ == "__main__":
    print(get_openai_response())


