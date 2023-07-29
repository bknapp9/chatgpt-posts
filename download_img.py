import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


SCOPES = ['https://www.googleapis.com/auth/drive.readonly']


def get_credentials():
    creds = None
    # The file name of the JSON file you downloaded from the Google Cloud Console
    credentials_file = 'credentials.json'

    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_file, SCOPES)
            creds = flow.run_local_server(port=8080)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return creds


def download_images_from_folder(folder_id, output_folder, r):
    # Authenticate using the service account credentials
    creds = get_credentials()
    service = build('drive', 'v3', credentials=creds)

    # Retrieve a list of files in the folder
    response = service.files().list(q=f"'{folder_id}' in parents and mimeType contains 'image/'",
                                    fields="files(id, name)").execute()
    files = response.get('files', [])

    # Create the output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Download each image from the folder
    counter = 0
    for file in files:
        if counter >= r:
            break
        else:
            file_id = file['id']
            file_name = file['name']

            txt_file = open('blacklist.txt', 'r')
            black_list = txt_file.readlines()

            if file_name + '\n' not in black_list:
                request = service.files().get_media(fileId=file_id)
                fh = io.FileIO(os.path.join(output_folder, file_name), 'wb')
                downloader = MediaIoBaseDownload(fh, request)

                done = False

                while not done:
                    status, done = downloader.next_chunk()
                    print('Download progress {0}'.format(status.progress() * 100))

                # fh.seek(0)
                #
                # with open(os.path.join('./Imagenes', file_name), 'wb') as f:
                #     f.write(fh.read())
                #     f.close()
                with open('blacklist.txt', 'a') as f:
                    f.write(file_name + '\n')
                    counter += 1

            elif len(black_list) > 63:
                with open('blacklist.txt', 'w'):
                    pass
                    
