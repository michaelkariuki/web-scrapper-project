from __future__ import print_function

import os.path
import traceback
import mimetypes
import urllib.parse as url_parse
import io
# import magic

from file_ops import *


from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload

# If modifying these scopes, delete the file token.json.
SCOPES = [
    'https://www.googleapis.com/auth/drive.metadata.readonly',
    'https://www.googleapis.com/auth/drive'
    ]

from main import download_loc
creds_path = os.path.join(os.getcwd(), 'Credentials', 'credentials.json')
metadata_file = 'g_drive_mt.json'

g_dict = {
    'MIME' : {
        'folder': 'application/vnd.google-apps.folder'
    },
    'QUERIES':{
        'get_folder_by_id' : lambda id: f"'{id}' in parents and trashed = false",
        'get_item' : lambda name, mime= None: f"name contains '{name}'" \
                    if mime == None else f"name contains '{name}' and mimeType={mime}"
    }
}
# ****************************************************************************************
def set_up_engine(creds_path = creds_path):
    creds = None

    if os.path.exists('token.json'):
        # print('token.json exists...')
        creds  = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                creds_path, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    return creds

# ****************************************************************************************
# function that gives me data about the files and folders in my google drive
# data : file name, id, mime type
# data : folder name, id
def get_metadata():
    creds = set_up_engine()

    try:
        service = build('drive', 'v3', credentials= creds)
        # query = "mimeType='application/vnd.google-apps.folder' or mimeType != 'application/vnd.google-apps.folder'"
        query = "'root' in parents and trashed = false"

        fields = 'nextPageToken, files(id, name, mimeType)'
        results = service.files().list(q=query, fields=fields).execute()

        items = results.get('files', [])
        items = sort_metadata(items)

        if not openJsonFile(metadata_file) == items:
            store_metadata(items)
        else:
            print(f"No changes detected, File : {metadata_file} upto date...")
    except HttpError:
        # TODO(developer) - Handle errors from drive API.
        print(traceback.format_exc())
# ****************************************************************************************
def sort_metadata(data: list) -> dict:
    result = {'folders': [], 'files' : []}

    for item in data:
        if item['mimeType'] == 'application/vnd.google-apps.folder':
            result['folders'].append(item)
        else:
            result['files'].append(item)
    
    return result
# ****************************************************************************************
def store_metadata(data: dict, filename: str = 'g_drive_mt'):
    json_data = convert_to_json(data)
    write_to_json_file(json_data, filename)
# ****************************************************************************************
def print_metadata(data= None):
    if not data:
        data = openJsonFile(metadata_file)
    
    for key in data.keys():
        print(f'\n****{key.upper()}****\n')
        for item in data[key]:
            print(f'NAME : {item["name"]}\nMIME : {item["mimeType"]}\nID: {item["id"]}\n')

# ****************************************************************************************
# NEXT UP :
# RETURN A DICT CONTAINING THE AN ITEM INFO YOU WANT FROM THE METADATA FILE (g_drive_mt.json)
def get_item_data(name: str, mimetype: str = None):
    metadata = openJsonFile(metadata_file)

    if mimetype:
        if mimetype == g_dict['MIME']['folder']:
            for item in metadata['folders']:
                if item['name'] == name:
                    return item
        else:
            for item in metadata['files']:
                if item['name'] == name:
                    return item
    
    for key in metadata.keys():
        for item in metadata[key]:
            if item['name'] == name:
                return item

    return None
# ****************************************************************************************
# PRINTING FOLDER CONTENTS
# only works for folders in parent directory 
def print_folder_contents(folder_id: str):
    creds = set_up_engine()
    try:
        service = build('drive', 'v3', credentials= creds)

        query = f"'{folder_id}' in parents"
        results = service.files().list(
            q=query, fields='nextPageToken, files(id, name, mimeType)').execute()

        items = results.get('files', [])

        if not items:
            print('No files found')
            return
        
        res = sort_metadata(items)
        print_metadata(res)

    except HttpError:
        # TODO(developer) - Handle errors from drive API.
        print(traceback.format_exc())
# ****************************************************************************************
def search_item(name: str, mimetype: str= None):
    creds = set_up_engine()
    res = {}
    try:
        service = build('drive', 'v3', credentials= creds)

        parsed_name = url_parse.quote(name)
        query = g_dict['QUERIES']['get_item'](parsed_name)
        results = service.files().list(
            q=query, fields='nextPageToken, files(id, name, mimeType, parents)').execute()

        items = results.get('files', [])
            
        res = sort_metadata(items) if items else res
        
        return res
    except HttpError:
        # TODO(developer) - Handle errors from drive API.
        print(traceback.format_exc())


# ****************************************************************************************
# CRUD OPERATIONS IN A SPECIFIC FOLDER*
# REQUIREMENT : Oauth permission (allow CRUD ops in consent screen (google cloud console)) ✔

# CRUD : Create file
def upload_item(file_name: str, file_path: str, folder_id: str= None):
    creds = set_up_engine()

    try:
        service = build('drive', 'v3', credentials= creds)

        if os.path.exists(file_path):
            # Create the metadata for the file you want to upload
            mime_type = mimetypes.guess_type(file_path)[0]
            mime_parts = mime_type.split('/')
            extension =  'txt' if mime_parts[1] ==  'plain' else mime_parts[1]

            if folder_id:
                metadata = {
                    'name': file_name,
                    'parents': [folder_id]
                }    
            else:
                metadata = {
                    'name': file_name
                }    

            
            # Use the files().create() method to upload the file
            media = MediaFileUpload(file_path, mimetype=mime_type)
            response = service.files().create(body=metadata, media_body=media, fields='id, name').execute()
            
            print(f'File : {response["name"]} created successfully ...\n')


    except HttpError:
        # TODO(developer) - Handle errors from drive API.
        print(traceback.format_exc())
# ****************************************************************************************
# CRUD : Read file
def read_item(item: dict, file_download_path: str= None): 
    if not file_download_path:
        file_download_path = os.path.join(download_loc, item['name'])  

    creds = set_up_engine()

    try:
        service = build('drive', 'v3', credentials= creds)

        if item['mimeType'] == 'text/plain':
            # Use the files().delete() method to delete the folder
            response = service.files().get_media(fileId=item['id']).execute()
            # Read the file's contents into a string
            content_string = response.decode()
            write_str_to_file(content_string, file_download_path)

        else:
            request = service.files().get_media(fileId=item['id'])
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            done = False

            while done is False:
                status, done = downloader.next_chunk()
                print(f"Download {int(status.progress() * 100)}")

            fh.seek(0)
            write_bin_to_file(fh, file_download_path)

        print(f"File: {item['name']} downloaded to {file_download_path}")

    except HttpError or IOError:
        traceback.format_exc()
# ****************************************************************************************
# CRUD : Update/edit file
# ISSUE : items in specific folders not stored in metadata, causes error
# need to work on figuring out how to upload to a folder and also root
def update_item(item: dict, new_file_path: str= None, new_file_name: str= None, new_folder_name: str= None):
    creds = set_up_engine()

    try:
        service = build('drive', 'v3', credentials= creds)

        if not os.path.isfile(new_file_path) and new_folder_name:
            folder_mt = {
                'name' : new_folder_name,
                'mimeType' : g_dict['MIME']['folder']
            }

            response = service.files().update(fileId=item['id'], body=folder_mt, fields='id').execute()
            print(response)
            print(f'File ID: {response["id"]} updated successfully ...')

        
        if new_file_path and os.path.exists(new_file_path):
            metadata = {'name': None}  
            mime_type = mimetypes.guess_type(new_file_path)[0]
            mime_parts = mime_type.split('/')
            extension =  'txt' if mime_parts[1] ==  'plain' else mime_parts[1]

            if new_file_name:
                metadata.update({'name': f"{new_file_name}.{extension}"})
            else:
                metadata.update({'name': item['name']})

            if item['parents']:
                metadata.update({'parents': item['parents'].pop()})
     
            media = MediaFileUpload(new_file_path, mimetype=mime_type)
            response = service.files().update(fileId=item['id'],body=metadata, media_body=media, fields='id').execute()

            print(response)
            print(f'File ID: {response["id"]} updated successfully ...')

    except HttpError:
        traceback.format_exc()

# ****************************************************************************************
# CRUD : Delete file
def delete_item(item: dict):
    creds = set_up_engine()

    try:
        service = build('drive', 'v3', credentials= creds)

        # Use the files().delete() method to delete the folder
        response = service.files().delete(fileId=item['id']).execute()

        # print(response)

    except HttpError:
        traceback.format_exc()
    finally:
        print(f"Name : {item['name']} deleted successfully ...")
        print(response)
        get_metadata()
