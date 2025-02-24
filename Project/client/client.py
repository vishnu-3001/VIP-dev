import requests
def downloadDocument(file_id):
    url = f"http://localhost:8000/api/v1/drive/download?file_id={file_id}"
    response = requests.get(url)
    try:
        return response.json()  
    except requests.exceptions.JSONDecodeError:
        print("Error: Response is not in JSON format.")
        return None
def extract():
    url=f"http://localhost:8000/api/v1/extract/extract"
    response=requests.get(url)
    if response.status_code == 200:
        return response.json()
    return {"error": "Failed to fetch logs", "status": response.status_code}

def dates_analysis():
    url=f"http://localhost:8000/api/v1/analysis/format"
    response=requests.get(url)
    if response.status_code==200:
        return response.json()
    return {"error":"Failed to analyze dates","status":response.status_code}

def collaborate(fileid: str):
    url = f"http://localhost:8000/api/v1/analysis/logs/{fileid}"  
    response = requests.get(url)  
    if response.status_code == 200:
        return response.json()
    return {"error": "Failed to analyze logs"}

def references():
    url=f"http://localhost:8000/api/v1/analysis/references"
    response=requests.get(url)
    if response.status_code==200:
        return response.json()
    return {"error":"Failed to analyze references"}


if __name__ == "__main__":
    # file_id = "1hDv1qgU-fhgGQpv3J9_YtCFXE4gJZILQRt4ZSvEBr9M"
    # file_data=downloadDocument(file_id)
    # extract()
    # print(dates_analysis())
    # print(collaborate(file_id))
    print(references())
    

    