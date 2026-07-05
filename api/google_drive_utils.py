"""Google Drive integration for payment-proof uploads.

Reads the service account JSON from an env var's CONTENT (not a file
path) since neither Cloud Run nor any host used here guarantees a
persistent filesystem path for secrets - see GOOGLE_SERVICE_ACCOUNT_JSON
in .env.example.
"""
import io
import json
import os

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

SCOPES = ["https://www.googleapis.com/auth/drive"]


def _get_drive_service():
    info = json.loads(os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"])
    creds = service_account.Credentials.from_service_account_info(info, scopes=SCOPES)
    return build("drive", "v3", credentials=creds)


def ensure_member_folder(member_code: str) -> str:
    """Returns the Drive folder ID for this member, creating it under the
    configured root folder if it doesn't already exist."""
    service = _get_drive_service()
    root_id = os.environ["GOOGLE_DRIVE_ROOT_FOLDER_ID"]
    query = (
        f"'{root_id}' in parents and "
        f"mimeType = 'application/vnd.google-apps.folder' and "
        f"name contains '{member_code}' and trashed = false"
    )
    results = service.files().list(q=query, fields="files(id, name)").execute()
    files = results.get("files", [])
    if files:
        return files[0]["id"]

    folder_metadata = {
        "name": member_code,
        "mimeType": "application/vnd.google-apps.folder",
        "parents": [root_id],
    }
    folder = service.files().create(body=folder_metadata, fields="id").execute()
    return folder["id"]


def upload_to_drive(member_code: str, file_name: str, file_bytes: bytes,
                     mime_type: str) -> dict:
    """Uploads file_bytes as file_name into the member's folder.
    Returns {"file_id": ..., "web_view_link": ...}."""
    service = _get_drive_service()
    folder_id = ensure_member_folder(member_code)

    file_metadata = {"name": file_name, "parents": [folder_id]}
    # MediaIoBaseUpload (not MediaFileUpload) because the source is an
    # in-memory byte buffer from an in-flight multipart upload, not a
    # path on disk.
    media = MediaIoBaseUpload(io.BytesIO(file_bytes), mimetype=mime_type, resumable=False)
    uploaded = service.files().create(
        body=file_metadata, media_body=media, fields="id, webViewLink"
    ).execute()
    return {"file_id": uploaded["id"], "web_view_link": uploaded.get("webViewLink", "")}
