import io
from Google import Create_Service
import os
from googleapiclient.http import MediaIoBaseDownload

CLIENT_SECRET_FILE = 'client_secrets.json'
API_NAME = 'drive'
API_VERSION = 'v3'
SCOPES = ['https://www.googleapis.com/auth/drive']

service = Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)


def download_image(r):
    folder_id = '13O0xJ2tOIWp53KNMH16wVcskR2tHB0fZ'
    query = f"'{folder_id}' in parents and mimeType contains 'image/'"
    counter = 0
    response = service.files().list(q=query).execute()
    files = response.get('files')
    files.extend(response.get('files'))

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
                fh = io.BytesIO()
                downloader = MediaIoBaseDownload(fd=fh, request=request)

                done = False

                while not done:
                    status, done = downloader.next_chunk()
                    print('Download progress {0}'.format(status.progress() * 100))

                fh.seek(0)

                with open(os.path.join('./Imagenes', file_name), 'wb') as f:
                    f.write(fh.read())
                    f.close()
                with open('blacklist.txt', 'a') as f:
                    f.write(file_name + '\n')
                    counter += 1
            elif len(black_list) > 63:
                with open('blacklist.txt', 'w'):
                    pass

