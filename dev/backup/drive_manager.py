import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ['https://www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_FILE = os.path.join(os.path.dirname(__file__), 'service_account.json')



def build_drive_service(service_account_file=SERVICE_ACCOUNT_FILE):
    credentials = service_account.Credentials.from_service_account_file(
        service_account_file,
        scopes=SCOPES,
    )
    return build('drive', 'v3', credentials=credentials)


def upload_backup(file_path, folder_id=None):
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f'File not found: {file_path}')

    service = build_drive_service()

    file_metadata = {
        'name': os.path.basename(file_path),
        'parents': [folder_id] if folder_id else [BACKUP_FOLDER_ID],
    }

    media = MediaFileUpload(file_path, resumable=True)

    uploaded_file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id',
        supportsAllDrives=True,
    ).execute()

    return uploaded_file.get('id')


def upload_to_folder(file_path, folder_id):
    """Upload a file to a specific Drive folder (used for WAL archives).

    Args:
        file_path (str): Local path to file.
        folder_id (str): Drive folder ID where the file will be placed.

    Returns:
        str: uploaded file ID
    """
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f'File not found: {file_path}')

    service = build_drive_service()

    file_metadata = {
        'name': os.path.basename(file_path),
        'parents': [folder_id],
    }

    media = MediaFileUpload(file_path, resumable=True)

    uploaded_file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id',
        supportsAllDrives=True,
    ).execute()

    return uploaded_file.get('id')