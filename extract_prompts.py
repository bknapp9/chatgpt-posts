import random
import os
import requests
import base64
from bs4 import BeautifulSoup
from googleapiclient.discovery import build
from google.oauth2 import service_account
from categories import categories_ids
from download_images import download_image
from creds import user, app_password
import openai


class ChatGPTHandler:
    def __init__(self):
        self.openai_api_key = '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'
        openai.api_key = self.openai_api_key

    def generate_chat_completion(self, role, content, temperature, max_tokens):
        completion = openai.ChatCompletion.create(
            model='gpt-4-1106-preview',
            messages=[{'role': role, 'content': content}],
            temperature=temperature,
            max_tokens=max_tokens
        )
        response = completion.choices[0].message.content
        html_response = BeautifulSoup(response, 'html.parser').prettify()
        return response, html_response

    def parse_html_tags(self, html_content):
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


class ImageHandler:
    @staticmethod
    def get_file_path(directory):
        file_paths = [os.path.join(root, file).replace('\\', '//') for root, _, files in os.walk(directory) for file in files]
        return file_paths

    @staticmethod
    def upload_image_wordpress(image_path):
        url = 'http://revistapyme21.cl/wp-json/wp/v2/media'
        data = open(image_path, 'rb').read()
        fileName = os.path.basename(image_path)
        res = requests.post(url='https://revistapyme21.cl/wp-json/wp/v2/media',
                            data=data,
                            headers={'Content-Type': 'image/jpg',
                                     'Content-Disposition': 'attachment; filename=%s' % fileName},
                            auth=(user, app_password))

        if res.status_code == 201:
            res_data = res.json()
            image_id = res_data['id']
            return image_id
        else:
            print('Error al subir la imagen:', res.text)
            return None


class WordpressHandler:
    @staticmethod
    def post(title, category, html_response, tags, image_id, api_url, wordpress_header):
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


class MainHandler:
    def __init__(self):
        self.counter = 0
        self.x = 2
        self.y = 3
        self.file_paths = []

    def process_data(self, SPREADSHEET_ID, sheet, api_url, wordpress_header):
        gpt_handler = ChatGPTHandler()
        image_handler = ImageHandler()
        wordpress_handler = WordpressHandler()
        directory = 'C:/Users/benja/Escritorio/tgin4ewijonwt34/ChatGPT Python/Imagenes'
        file_paths = image_handler.get_file_path(directory)
        while True:
            if self.counter >= 2:
                break
            else:
                result = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                            range=f'BASE GPT!B{self.x}:L{self.y}').execute()
                image_urls_results = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                                        range=f'BASE GPT!K{self.x}:K{self.y}').execute()
                values = result.get('values', [])
                image_urls_values = image_urls_results.get('values', [])
                image_urls = image_urls = [url for sublist in image_urls_values for url in sublist]
                # res = sheet.values().clear(spreadsheetId=SPREADSHEET_ID,
                #                            range=f'BASE GPT!A{self.x}:L{self.y}').execute()
                if values == []:
                    x = x + 2
                    y = y + 2
                for row in values:
                    if row == []:
                        values.pop(0)
                    else:
                        model = row[0]
                        max_tokens = 3000
                        temperature = float(row[2])
                        role = row[3]
                        category_name = row[5]
                        content = row[10]

                        category_id = categories_ids[category_name]

                        response, html_response = gpt_handler.generate_chat_completion(role, content, temperature, max_tokens)
                        title, tags = gpt_handler.parse_html_tags(html_response)
                        directory = 'C:/Users/benja/Escritorio/tgin4ewijonwt34/ChatGPT Python/Imagenes'

                        file_paths = image_handler.get_file_path(directory)
                        SAVE_DIRECTORY = './Imagenes'
                        CLIENT_ID = 'b97d1b989ef0d40'
                        if len(file_paths) == 0:
                            for idx, url in enumerate(image_urls):
                                download_image(url, os.path.join(SAVE_DIRECTORY, f'image{idx + 1}.jpg'))
                                print(f"Image {idx + 1} downloaded successfully to {SAVE_DIRECTORY}.")
                        file_paths = image_handler.get_file_path(directory)
                        image_id = image_handler.upload_image_wordpress(file_paths[0])


                        response = wordpress_handler.post(title, category_id, response, tags, image_id, api_url, wordpress_header)

                        if response.status_code == 201:
                            print('Post creado')
                        else:
                            print('Error al crear el post:', response.text)
                        os.remove(file_paths[0])
                        self.counter += 1

# Usage:
if __name__ == "__main__":
    main_handler = MainHandler()
    main_handler.process_data()
