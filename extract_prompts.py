import random
from categories import categories_ids
from googleapiclient.discovery import build
from google.oauth2 import service_account
import json
import openai
from bs4 import BeautifulSoup
import requests
import base64
from download_img import download_image
import os
from creds import user, app_password

file_paths = []


def generate_chat_completion(role, content, temperature, max_tokens):
    # OpenAI API key
    openai.api_key = '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'

    # Crear el query a Chat GPT
    completion = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        messages=[{'role': role, 'content': content}],
        temperature=temperature,
        max_tokens=max_tokens
    )

    response = completion.choices[0].message.content
    html_response = BeautifulSoup(response, 'html.parser').prettify()

    print('Query creada')
    return response, html_response


def parse_html_tags(html_content):
    # Encontrar las metatags y el title
    soup = BeautifulSoup(html_content, 'html.parser')
    metatags = soup.find_all('meta')
    tags = []
    for tag in metatags:
        tag_name = tag.get('name')
        tag_content = tag.get('content')
        if tag_name and tag_content:
            tags.append({'name': tag_name, 'content': tag_content})
    title = soup.find('h1').text.strip()

    return title, tags


def get_file_path(directory):

    # Extraer una ruta de imagen aleatoria
    file_paths = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            image_path = os.path.join(root, file).replace('\\', '//')
            file_paths.append(image_path)

    if file_paths:
        return random.choice(file_paths), file_paths
    else:
        return None


def upload_image_wordpress(image_path):

    # Subir las imagenes a Wordpress
    url = 'http://revistapyme21.cl/wp-json/wp/v2/media'
    data = open(image_path, 'rb').read()
    fileName = os.path.basename(image_path)
    res = requests.post(url='https://revistapyme21.cl/wp-json/wp/v2/media',
                        data=data,
                        headers={'Content-Type': 'image/jpg',
                                 'Content-Disposition': 'attachment; filename=%s' % fileName},
                        auth=(user, app_password))

    # Extraer el id de imagen
    if res.status_code == 201:
        res_data = res.json()
        image_id = res_data['id']
        return image_id
    else:
        print('Error al subir la imagen:', res.text)
        image_id = None


def post(title, category, html_response, tags, image_id, api_url, wordpress_header):
    # Crear el post con los criterios requeridos
    data = {
        'title': title,
        'author': 2,
        'status': 'publish',
        'categories': [category],
        'content': html_response,
        'meta': tags,
        'featured_media': image_id
    }
    response = requests.post(api_url, headers=wordpress_header, json=data)
    return response


if __name__ == '__main__':
    n = 2
    x = 11
    SERVICE_ACCOUNT_FILE = 'credentials.json'
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

    creds = None
    creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)

    # The ID and range of a sample spreadsheet.
    SAMPLE_SPREADSHEET_ID = '136Q7VWIgGdY7imDMRa_ckYV_0wFu0KgDm03vr9dXCsg'

    service = build('sheets', 'v4', credentials=creds)

    sheet = service.spreadsheets()

    api_url = 'https://revistapyme21.cl/wp-json/wp/v2/posts'
    wordpress_user = user
    wordpress_password = app_password
    wordpress_credentials = wordpress_user + ':' + wordpress_password
    wordpress_token = base64.b64encode(wordpress_credentials.encode())
    wordpress_header = {'Authorization': 'Basic ' + wordpress_token.decode('utf-8')}

    counter = 0
    while True:
        if counter >= 10:
            break
        else:
            result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                        range=f'BASE GPT!B{n}:L{x}').execute()
            values = result.get('values', [])

            res = sheet.values().clear(spreadsheetId=SAMPLE_SPREADSHEET_ID, range=f'BASE GPT!A{n}:L{x}').execute()
            n = n + 10
            x = x + 10

            for row in values:
                if values[0] == '':
                    break
                else:
                    model = row[0]
                    max_tokens = 3000
                    temperature = float(row[2])
                    role = row[3]
                    category_name = row[5]
                    content = row[9]

                    category_id = categories_ids[category_name]

                    response, html_response = generate_chat_completion(role, content, temperature, max_tokens)
                    title, tags = parse_html_tags(html_response)
                    directory = 'C:/Users/benja/Escritorio/tgin4ewijonwt34/ChatGPT Python/Imagenes'

                    if len(file_paths) >= 1:
                        pass
                    else:
                        folder_id = '13O0xJ2tOIWp53KNMH16wVcskR2tHB0fZ'  # Replace with the ID of the Google Drive folder
                        credentials_path = 'credentials.json'  # Replace with the path to your service account credentials
                        output_folder = './Imagenes'  # Replace with the desired output folder

                        r = 10
                        download_images_from_folder(folder_id, output_folder, r)

                    file_path, file_paths = get_file_path(directory)
                    image_id = upload_image_wordpress(file_path)
                    # response = post(title, category_id, html_response, tags, image_id, api_url, wordpress_header)

                    if response.status_code == 201:
                        print('Post creado')
                    else:
                        print('Error al crear el post:', response.text)
                    os.remove(file_path)

