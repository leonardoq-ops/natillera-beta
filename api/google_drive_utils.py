"""Google Drive integration for payment-proof uploads.

Uses Application Default Credentials (ADC) rather than a downloadable
service-account JSON key: the target org has an Organization Policy
(iam.disableServiceAccountKeyCreation) blocking key creation entirely
(Google's own recommended default, since key files are a standing
security liability). On Cloud Run, ADC is satisfied automatically by
attaching the service account directly to the Cloud Run service (its
"Service account" setting) - google.auth.default() then picks up
credentials from Cloud Run's metadata server with no key file ever
existing. For local dev, `gcloud auth application-default login`
achieves the same thing using your own user credentials.
"""
import io
import os

import google.auth
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

SCOPES = ["https://www.googleapis.com/auth/drive"]


def _get_drive_service():
    creds, _ = google.auth.default(scopes=SCOPES)
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
