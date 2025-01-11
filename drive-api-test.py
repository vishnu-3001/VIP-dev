from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES=['https://www.googleapis.com/auth/drive']

def main():
    creds=None
    try:
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    except Exception:
        flow=InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
        creds=flow.run_local_server(port=55342)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    service=build('drive', 'v3', credentials=creds)
    print("Fetching files from your google drive...")
    results=service.files().list(
        q="mimeType='application/vnd.openxmlformats-officedocument.wordprocessingml.document'",
        spaces='drive',
        fields='files(id, name,version)'
    ).execute()
    items=results.get('files', [])
    if not items:
        print('No files found.')
    else:
        file_id='14r5KXdj3KgvM4o4P7vQz3jQVUeWLJbKyU1NlE4-Yphc'
        revisions=service.revisions().list(fileId=file_id,fields='revisions(id, modifiedTime, lastModifyingUser(displayName, emailAddress))').execute()
        accumulated_data={}
        for revision in revisions.get('revisions', []):
            # print(revision)
            email=revision['lastModifyingUser']['displayName']
            print(email)
            modifiedTime=revision['modifiedTime']
            print(modifiedTime)
            if email not in accumulated_data:
                accumulated_data[email]=[]
            accumulated_data[email].append(modifiedTime)
        print(accumulated_data)
if __name__ == '__main__':
    main()
