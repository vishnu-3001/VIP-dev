import requests
def get_collaboration_analysis(file_id: str):
    response = requests.get(f"http://localhost:8000/api/v1/analysis/logs?file_id={file_id}")
    if response.status_code == 200:
        return response.json()
    return {"error": "Failed to fetch logs", "status": response.status_code}
def get_format_analysis(file_id:str):
    response=requests.get(f"http://localhost:8000/api/v1/analysis/format?file_id={file_id}")
    if response.status_code==200:
        return response.json()
    return {"error":"Failed to download the file", "status":response.status_code}
def get_summary():
    response=requests.get(f"http://localhost:8000/api/v1/content/summary")
    if response.status_code==200:
        return response.json()
    return {"error":"Failed to get summary","status":response.status_code}

if __name__ == "__main__":
    file_id = "1T5IBAzS2_6RrivL-hIsKeA2JQh65a3WDrZXconrEYcY"
    print(get_collaboration_analysis(file_id))
    print(get_format_analysis(file_id))
    print(get_summary())