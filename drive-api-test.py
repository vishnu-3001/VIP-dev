from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES=['https://www.googleapis.com/auth/drive']

def main():
    file_name=''
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
    # results = service.files().list( fields="files(id, name)").execute()
    # items = results.get('files', [])
    if not items:
        print('No files found.')
    else:
        # print(items)
        file_id='1qNTGWV6uzJby2UHpto3cS7OHuY4_bIyYYEFMzqdkUic'
        print(f"found file '{file_name} with id: {file_id}'")
        revisions=service.revisions().list(fileId=file_id,fields='revisions(id, modifiedTime, lastModifyingUser(displayName, emailAddress))').execute()
        for revision in revisions.get('revisions', []):
            print(revision)
            # print(f"Revision ID: {revision['id']}")
            # print(f"Modified Time: {revision['modifiedTime']}")
            # print(revision)
            # print(f"Last Modifier: {revision['lastModifyingUser']['displayName']}")
        # print('Files:')
        # for item in items:
        #     print(f"{item['name']}  ({item['version']})")
if __name__ == '__main__':
    main()