import requests
def downloadDocument(file_id):
    url = f"http://localhost:8000/api/v1/drive/download?file_id={file_id}"
    response = requests.get(url)
    try:
        return response.json()  
    except requests.exceptions.JSONDecodeError:
        print("Error: Response is not in JSON format.")
        return None
def processText():
    url=f"http://localhost:8000/api/v1/extract/process"
    response=requests.get(url)
    if response.status_code == 200:
        return response.json()
    return {"error": "Failed to fetch logs", "status": response.status_code}

if __name__ == "__main__":
    # file_id = "1ptGJPgCJj0sGWRMtQXIgVcOBaJ3GP3hgs9xwzPFFqr8"
    # file_data=downloadDocument(file_id)
    processText()
    

    