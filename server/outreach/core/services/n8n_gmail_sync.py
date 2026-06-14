import copy
import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path

from core.exceptions import ExpectedError
from core.models import GmailConnection
from core.services import n8n_client

logger = logging.getLogger("n8n_gmail_sync")

WORKFLOW_TEMPLATE_CANDIDATES = (
    Path(__file__).resolve().parents[2] / "n8n" / "workflows" / "gmail-inbound-reply.json",
    Path(__file__).resolve().parents[3] / "n8n" / "workflows" / "gmail-inbound-reply.json",
)


def _workflow_template_path() -> Path:
    for path in WORKFLOW_TEMPLATE_CANDIDATES:
        if path.is_file():
            return path
    raise ExpectedError("Gmail workflow template not found (gmail-inbound-reply.json)")


def _client_id() -> str:
    return (os.environ.get("GOOGLE_OAUTH_CLIENT_ID") or "").strip()


def _client_secret() -> str:
    return (os.environ.get("GOOGLE_OAUTH_CLIENT_SECRET") or "").strip()


def _credential_name(conn: GmailConnection) -> str:
    label = conn.google_email or f"user {conn.user_id}"
    return f"SalesMind Gmail — {label}"


def _workflow_name(user_id: int) -> str:
    return f"SalesMind — Gmail Inbound Reply (user {user_id})"


def _find_workflow_id_by_name(name: str) -> str:
    for wf in n8n_client.list_workflows():
        if (wf.get("name") or "") == name:
            return str(wf.get("id") or "")
    return ""


def _gmail_credential_data(conn: GmailConnection) -> dict:
    expiry_date = int(datetime.now(timezone.utc).timestamp() * 1000) + 3600 * 1000
    if conn.expires_at:
        expiry_date = int(conn.expires_at.timestamp() * 1000)

    access_token = conn.access_token or ""
    refresh_token = conn.refresh_token or ""
    scope = conn.scope or ""

    # n8n public API schema for gmailOAuth2 only allows a small set of keys.
    # Tokens must live under oauthTokenData (not accessToken/refreshToken at top level).
    return {
        "serverUrl": "https://oauth2.googleapis.com",
        "clientId": _client_id(),
        "clientSecret": _client_secret(),
        "sendAdditionalBodyProperties": False,
        "additionalBodyProperties": "",
        "oauthTokenData": {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "scope": scope,
            "token_type": "Bearer",
            "expiry_date": expiry_date,
        },
    }


def _apply_workflow_credentials(workflow: dict, *, credential_id: str, credential_name: str, user_id: int) -> dict:
    wf = copy.deepcopy(workflow)
    cred_ref = {"gmailOAuth2": {"id": credential_id, "name": credential_name}}
    for node in wf.get("nodes", []):
        if node.get("type") in ("n8n-nodes-base.gmailTrigger", "n8n-nodes-base.gmail"):
            node["credentials"] = cred_ref
        if node.get("name") == "Handle Reply":
            body = node.get("parameters", {}).get("jsonBody", "")
            node.setdefault("parameters", {})["jsonBody"] = body.replace(
                "user_id: 0",
                f"user_id: {user_id}",
                1,
            )
    return wf


def _load_workflow_template(user_id: int, credential_id: str, credential_name: str) -> dict:
    template_path = _workflow_template_path()
    with template_path.open(encoding="utf-8") as f:
        template = json.load(f)

    workflow = _apply_workflow_credentials(template, credential_id=credential_id, credential_name=credential_name, user_id=user_id)
    workflow["name"] = _workflow_name(user_id)
    return workflow


def _ensure_credential(conn: GmailConnection, cred_name: str, cred_data: dict) -> str:
    credential_id = (conn.n8n_credential_id or "").strip()
    if credential_id:
        try:
            n8n_client.update_credential(credential_id, name=cred_name, data=cred_data)
            return credential_id
        except ExpectedError as e:
            if "404" not in str(e):
                raise
            logger.warning("Stored n8n credential %s missing; creating a new one", credential_id)
            credential_id = ""

    created = n8n_client.create_credential(name=cred_name, cred_type="gmailOAuth2", data=cred_data)
    credential_id = str(created.get("id") or "")
    if not credential_id:
        raise ExpectedError("n8n did not return a credential id")
    conn.n8n_credential_id = credential_id
    return credential_id


def _ensure_workflow(conn: GmailConnection, *, credential_id: str, cred_name: str) -> str:
    workflow_id = (conn.n8n_workflow_id or "").strip()
    workflow_name = _workflow_name(conn.user_id)

    if not workflow_id:
        workflow_id = _find_workflow_id_by_name(workflow_name)
        if workflow_id:
            conn.n8n_workflow_id = workflow_id

    if workflow_id:
        try:
            wf = n8n_client.get_workflow(workflow_id)
            nodes = _apply_workflow_credentials(
                {"nodes": wf.get("nodes") or []},
                credential_id=credential_id,
                credential_name=cred_name,
                user_id=conn.user_id,
            )["nodes"]
            n8n_client.update_workflow(workflow_id, nodes=nodes, name=workflow_name)
            n8n_client.activate_workflow(workflow_id)
            return workflow_id
        except ExpectedError as e:
            if "404" not in str(e):
                raise
            logger.warning("Stored n8n workflow %s missing; creating a new one", workflow_id)
            workflow_id = ""

    payload = _load_workflow_template(conn.user_id, credential_id, cred_name)
    created_wf = n8n_client.create_workflow(
        name=payload["name"],
        nodes=payload["nodes"],
        connections=payload["connections"],
        settings=payload.get("settings"),
    )
    workflow_id = str(created_wf.get("id") or "")
    if not workflow_id:
        raise ExpectedError("n8n did not return a workflow id")
    conn.n8n_workflow_id = workflow_id
    n8n_client.activate_workflow(workflow_id)
    return workflow_id


def sync_gmail_to_n8n(conn: GmailConnection) -> GmailConnection:
    """Push Gmail tokens to n8n and ensure a per-user inbound workflow exists."""
    if not conn.refresh_token:
        raise ExpectedError("Gmail is not connected")

    if not n8n_client.n8n_configured():
        raise ExpectedError("n8n API is not configured. Set N8N_API_KEY in server/.env.")

    cred_name = _credential_name(conn)
    cred_data = _gmail_credential_data(conn)

    try:
        credential_id = _ensure_credential(conn, cred_name, cred_data)
        _ensure_workflow(conn, credential_id=credential_id, cred_name=cred_name)

        conn.n8n_sync_error = ""
        conn.n8n_synced_at = datetime.now(timezone.utc)
        conn.save(
            update_fields=[
                "n8n_credential_id",
                "n8n_workflow_id",
                "n8n_sync_error",
                "n8n_synced_at",
                "updated_at",
            ]
        )
    except ExpectedError as e:
        conn.n8n_sync_error = str(e)[:500]
        conn.save(update_fields=["n8n_sync_error", "updated_at"])
        raise
    except Exception as e:
        logger.exception("n8n Gmail sync failed for user_id=%s", conn.user_id)
        conn.n8n_sync_error = str(e)[:500]
        conn.save(update_fields=["n8n_sync_error", "updated_at"])
        raise ExpectedError(f"n8n sync failed: {e}") from e

    return conn


def teardown_n8n_gmail(conn: GmailConnection) -> None:
    if not n8n_client.n8n_configured():
        return

    if conn.n8n_workflow_id:
        try:
            n8n_client.delete_workflow(conn.n8n_workflow_id)
        except ExpectedError:
            logger.warning("Could not delete n8n workflow %s", conn.n8n_workflow_id)

    if conn.n8n_credential_id:
        try:
            n8n_client.delete_credential(conn.n8n_credential_id)
        except ExpectedError:
            logger.warning("Could not delete n8n credential %s", conn.n8n_credential_id)
