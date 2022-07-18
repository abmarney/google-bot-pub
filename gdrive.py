from __future__ import print_function
import os.path
from dotenv import load_dotenv
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
import io
import random
load_dotenv()

# IF SCOPES CHANGE, DELETE TOKEN AND REAUTHENTICATE

# handles access to google drive by managing credentials and manipulating file objects
#
class gdrive:    

    # initializes gdrive class, most input given from .env file
    #
    def __init__(self):
        self.UPLOAD_FOLDER_ID = os.getenv('UPLOAD_FOLDER')
        self.WEBM_FOLDER_ID = os.getenv('WEBM_FOLDER')
        self.WAV_FOLDER_ID = os.getenv('WAV_FOLDER')
        self.BASE_FILENAME = os.getenv('BASE_FILENAME')
        self.filename = ''
        self.SCOPES = [
            'https://www.googleapis.com/auth/drive.metadata.readonly',
            'https://www.googleapis.com/auth/drive'
            ]
        self.creds = None
        self.service = None
        self.newCredsFlag = 0
        self.fields = ''
        self.id = ''

        self.service = build('drive', 'v3', credentials=self.creds)

    # generate new credentials or refresh the current token if possible
    # newCredsFlag used to control additional calls within a single branching task
    #
    def new_creds(self):
        if self.newCredsFlag == 0:
            if os.path.exists('token.json'):
                self.creds = Credentials.from_authorized_user_file('token.json',self.SCOPES)
            if not self.creds or not self.creds.valid:
                if self.creds and self.creds.expired and self.creds.refresh_token:
                    self.creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', self.SCOPES)
                    self.creds = flow.run_local_server(port=8080)
                with open('token.json', 'w') as token:
                    token.write(self.creds.to_json())
            self.service = build(
                'drive', 
                'v3', 
                credentials=self.creds
                )
            self.newCredsFlag = 1



    # deletes a file using its id
    #   id = id of the file to delete
    def delete_file(self, id):
        self.new_creds()
        self.service.files().delete(fileId=id).execute()
        self.newCredsFlag = 0

    # downloads the requested file based on the type given.
    #   fileName = requested file name
    #   type = requested file type
    #
    def download_file(self, fileName, type):
        self.new_creds()
        if (type == 'webm'):
            results = self.service.files().list(
                q="'{}' in parents".format(self.WEBM_FOLDER_ID)
                ).execute()
        elif (type == 'wav'):
            results = self.service.files().list(
                q="'{}' in parents".format(self.WAV_FOLDER_ID)
                ).execute()            
        items = results.get('files', [])
        for x in items:
            if x['name'].lower() == (fileName + '.' + type):
                fullName = self.BASE_FILENAME + x['name']
                request = self.service.files().get_media(fileId=x['id'])
                file = io.FileIO(fileName, 'wb')
                downloader = MediaIoBaseDownload(file, request)
                done = False
                while done is False:
                    done = downloader.next_chunk()
                self.newCredsFlag = 0
                return fullName
        self.newCredsFlag = 0
        return 0

    # retrieves a random file using a given type
    #   type = given file type
    #
    def random_file(self, type):
        self.new_creds()
        if (type == 'webm'):
            results = self.service.files().list(
                pageSize=1000,
                q="'{}' in parents".format(self.WEBM_FOLDER_ID)
                ).execute()
        elif (type == 'wav'):
            results = self.service.files().list(
                pageSize=1000,
                q="'{}' in parents".format(self.WAV_FOLDER_ID)
                ).execute()
        items = results.get('files',[])
        ran = random.randint(1,len(items))-1
        link = self.retrieve_file(str(items[ran]['name'].lower()), type)
        return link

    # retrieves a file using a given file name and file type
    #   fileName = given file name
    #   type = given file type
    #
    def retrieve_file(self, fileName, type):
        self.new_creds()
        if (type == 'webm'):
            results = self.service.files().list(
                pageSize=1000,
                q="'{}' in parents".format(self.WEBM_FOLDER_ID)
                ).execute()
        elif (type == 'wav'):
            results = self.service.files().list(
                pageSize=1000,
                q="'{}' in parents".format(self.WAV_FOLDER_ID)
                ).execute()
        items = results.get('files',[])
        for x in items:
            if (x['name'].lower() == fileName):
                self.newCredsFlag = 0
                return 'https://drive.google.com/file/d/'+ x['id'] + '/view?usp=sharing'
        self.newCredsFlag = 0
        return 0

    # uploads a given file using the name and type given.
    #   fileName = given file name
    #   type = given file type
    #
    def upload_file(self, fileName, type):
        self.new_creds()
        if type == 'webm':
            file_metadata = {
                'name':fileName, 
                'parents':self.WEBM_FOLDER_ID
                }
        elif type == 'wav':
            file_metadata = {
                'name':fileName, 
                'parents':self.WAV_FOLDER_ID
                }
        fullName = self.BASE_FILENAME + fileName
        media = MediaFileUpload(fullName)
        file = self.service.files().create(
            body=file_metadata,
            media_body = media, 
            fields = 'id, webViewLink'
            ).execute()
        print('File Uploaded.')
        self.newCredsFlag = 0
        return file['webViewLink']