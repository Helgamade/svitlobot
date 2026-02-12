"""
Tuya Cloud API client (EU). Get token then device status.
Signature: https://developer.tuya.com/en/docs/iot/new-singnature?id=Kbw0q34cs2e5g
"""
from __future__ import absolute_import
import hashlib
import hmac
import time
import uuid
from typing import Dict, List, Optional
import requests

EMPTY_BODY_SHA256 = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"


def _sign(secret: str, payload: str) -> str:
    return hmac.new(
        secret.encode("utf-8"),
        payload.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest().upper()


def _request(
    method: str,
    path: str,
    base_url: str,
    access_id: str,
    access_secret: str,
    access_token: Optional[str] = None,
    query: Optional[Dict] = None,
) -> dict:
    t = str(int(time.time() * 1000))
    nonce = uuid.uuid4().hex

    url_path = path
    if query:
        parts = sorted(query.items(), key=lambda x: x[0])
        url_path = path + "?" + "&".join(f"{k}={v}" for k, v in parts)

    # stringToSign = Method + \n + Content-SHA256 + \n + Optional_Headers + \n + URL
    optional = ""  # no custom signature headers
    string_to_sign = f"{method}\n{EMPTY_BODY_SHA256}\n{optional}\n{url_path}"

    if access_token is None:
        # Token API
        str_to_hash = access_id + t + nonce + string_to_sign
    else:
        # General API
        str_to_hash = access_id + access_token + t + nonce + string_to_sign

    sign = _sign(access_secret, str_to_hash)

    headers = {
        "client_id": access_id,
        "sign": sign,
        "sign_method": "HMAC-SHA256",
        "t": t,
        "nonce": nonce,
    }
    if access_token is not None:
        headers["access_token"] = access_token

    r = requests.get(
        f"{base_url}{url_path}" if not url_path.startswith("http") else url_path,
        headers=headers,
        timeout=15,
    )
    r.raise_for_status()
    return r.json()


def get_token(base_url: str, access_id: str, access_secret: str) -> str:
    """Get access token for Tuya Cloud."""
    data = _request(
        "GET",
        "/v1.0/token?grant_type=1",
        base_url,
        access_id,
        access_secret,
        access_token=None,
    )
    if not data.get("success"):
        raise RuntimeError(f"Tuya token error: {data}")
    result = data.get("result", {})
    token = result.get("access_token")
    if not token:
        raise RuntimeError(f"No access_token in response: {data}")
    return token


def get_device_status(
    base_url: str,
    access_id: str,
    access_secret: str,
    access_token: str,
    device_id: str,
) -> List[dict]:
    """GET /v1.0/iot-03/devices/{device_id}/status. Returns list of {code, value}."""
    path = f"/v1.0/iot-03/devices/{device_id}/status"
    data = _request(
        "GET",
        path,
        base_url,
        access_id,
        access_secret,
        access_token=access_token,
    )
    if not data.get("success"):
        raise RuntimeError(f"Tuya device status error: {data}")
    return data.get("result", [])
