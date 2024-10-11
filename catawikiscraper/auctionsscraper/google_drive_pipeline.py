from google.oauth2 import service_account
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
import requests
import io
from urllib.parse import urlparse
from scrapy.http import Request
from googleapiclient.http import MediaIoBaseUpload


class GoogleDrivePipeline:
    def __init__(self, client_email, private_key, folder_ids):
        credentials = service_account.Credentials.from_service_account_info(
            {
                "type": "service_account",
                "client_email": client_email,
                "private_key": private_key,
                "token_uri": "https://oauth2.googleapis.com/token",
            })

        self.service = build("drive", "v3", credentials=credentials)
        self.folder_ids = folder_ids

    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings
        client_email = settings.get("GOOGLE_SERVICE_ACCOUNT_CLIENT_EMAIL")
        private_key = settings.get("GOOGLE_SERVICE_ACCOUNT_PRIVATE_KEY")
        folder_ids = settings.get("GOOGLE_DRIVE_FOLDER_IDS")
        return cls(client_email, private_key, folder_ids)

    def process_item(self, item, spider):
        image_url = item.get('highlight_image_url')
        if not image_url:
            return item

        type = item.get('type')
        folder_id = self.folder_ids.get(type)

        if not folder_id:
            print(f"No folder found for category {type}, skipping upload.")
            return item

        try:
            file_content = requests.get(image_url).content
            file_name = image_url.rsplit('/', 1)[-1]
            media = MediaIoBaseUpload(io.BytesIO(
                file_content), mimetype='image/jpeg', resumable=True)
            file_metadata = {'name': file_name, 'parents': [folder_id]}
            file = self.service.files().create(
                body=file_metadata, media_body=media, fields='id').execute()
            file_id = file.get("id")
            print(f"Uploaded file {file_name} with id {file_id}")
            item['file_name'] = file_name
            item[
                'highlight_image_url'] = f'=IMAGE("https://drive.google.com/uc?export=view&id={file_id}",1)'
        except HttpError as error:
            print(
                f"An error occurred while uploading image {image_url}: {error}")

        return item
