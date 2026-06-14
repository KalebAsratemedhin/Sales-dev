import logging
import os
from datetime import datetime, timedelta, timezone

import requests

from core.exceptions import ExpectedError, TransientError

logger = logging.getLogger("n8n_client")

DEFAULT_BASE_URL = "http://n8n:5678"


def n8n_configured() -> bool:
    return bool(_api_key() and _base_url())


def _base_url() -> str:
    return (os.environ.get("N8N_API_URL") or DEFAULT_BASE_URL).rstrip("/")


def _api_key() -> str:
    return (os.environ.get("N8N_API_KEY") or "").strip()


def _headers() -> dict:
    return {
        "X-N8N-API-KEY": _api_key(),
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


def _request(method: str, path: str, *, json: dict | None = None) -> dict:
    if not n8n_configured():
        raise ExpectedError("n8n API is not configured. Set N8N_API_KEY (and optionally N8N_API_URL).")

    url = f"{_base_url()}/api/v1{path}"
    try:
        resp = requests.request(method, url, headers=_headers(), json=json, timeout=30)
    except requests.RequestException as e:
        raise TransientError(f"n8n API request failed: {e}") from e

    if resp.status_code >= 400:
        body = (resp.text or "")[:500]
        raise ExpectedError(f"n8n API {method} {path} failed ({resp.status_code}): {body}")

    if not resp.content:
        return {}
    return resp.json()


def create_credential(*, name: str, cred_type: str, data: dict) -> dict:
    return _request("POST", "/credentials", json={"name": name, "type": cred_type, "data": data})


def update_credential(credential_id: str, *, name: str | None = None, data: dict | None = None) -> dict:
    payload: dict = {}
    if name is not None:
        payload["name"] = name
    if data is not None:
        payload["data"] = data
    return _request("PATCH", f"/credentials/{credential_id}", json=payload)


def delete_credential(credential_id: str) -> None:
    _request("DELETE", f"/credentials/{credential_id}")


def create_workflow(*, name: str, nodes: list, connections: dict, settings: dict | None = None) -> dict:
    payload = {
        "name": name,
        "nodes": nodes,
        "connections": connections,
        "settings": settings or {"executionOrder": "v1"},
    }
    return _request("POST", "/workflows", json=payload)


def list_workflows(*, limit: int = 250) -> list[dict]:
    result = _request("GET", f"/workflows?limit={limit}")
    if isinstance(result, dict):
        data = result.get("data")
        if isinstance(data, list):
            return data
    if isinstance(result, list):
        return result
    return []


def update_workflow(workflow_id: str, *, nodes: list | None = None, name: str | None = None) -> dict:
    payload: dict = {}
    if nodes is not None:
        payload["nodes"] = nodes
    if name is not None:
        payload["name"] = name
    return _request("PATCH", f"/workflows/{workflow_id}", json=payload)


def activate_workflow(workflow_id: str) -> dict:
    return _request("POST", f"/workflows/{workflow_id}/activate")


def deactivate_workflow(workflow_id: str) -> dict:
    return _request("POST", f"/workflows/{workflow_id}/deactivate")


def delete_workflow(workflow_id: str) -> None:
    try:
        deactivate_workflow(workflow_id)
    except ExpectedError:
        logger.warning("Could not deactivate n8n workflow %s before delete", workflow_id)
    _request("DELETE", f"/workflows/{workflow_id}")


def get_workflow(workflow_id: str) -> dict:
    return _request("GET", f"/workflows/{workflow_id}")
