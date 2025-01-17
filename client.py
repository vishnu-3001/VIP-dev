import requests

def get_collaboration_analysis(file_id):
    response = requests.get(f"http://localhost:8000/logs?file_id={file_id}")
    
    if response.status_code == 200:
        return response.json()
    else:
        return {
            "error": "Failed to get response",
            "status_code": response.status_code,
            "detail": response.text
        }

if __name__ == "__main__":
    file_id = "14r5KXdj3KgvM4o4P7vQz3jQVUeWLJbKyU1NlE4-Yphc"
    print(get_collaboration_analysis(file_id))
