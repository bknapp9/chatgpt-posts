import os
import requests


# Function to download an image from the URL and save it to a custom path
def download_image(url, save_path):
    response = requests.get(url)
    with open(save_path, 'wb') as file:
        file.write(response.content)


'''
# Create the save location directory if it doesn't exist
if not os.path.exists(save_location):
    os.makedirs(save_location)

# Read the uploaded image URLs from the text file
uploaded_image_urls = []
with open('uploaded_image_urls.txt', 'r') as file:
    uploaded_image_urls = [url.strip() for url in file.readlines()]
'''
