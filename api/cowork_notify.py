"""POSTs a task-creation payload to the external Cowork webhook.
COWORK_WEBHOOK_URL is an opaque secret filled in later by the user;
this module has no knowledge of what Cowork actually is."""
import os

import httpx


def notify_cowork(member_code: str, month: str, proof_url: str) -> None:
    webhook_url = os.environ.get("COWORK_WEBHOOK_URL")
    if not webhook_url:
        return  # not configured yet - fail open, never block the upload flow on this

    payload = {
        "action": "create_task",
        "assignee": os.environ.get("ADMIN_EMAIL", ""),
        "title": f"Verificar comprobante de pago — {member_code} ({month})",
        "description": f"Comprobante subido para {member_code}, mes {month}. Ver: {proof_url}",
        "priority": "medium",
        "tags": ["natillera", "verificacion-pago"],
        "due_date": None,
    }
    try:
        httpx.post(webhook_url, json=payload, timeout=10)
    except httpx.HTTPError:
        pass  # best-effort notification; never fail the upload because Cowork is down
