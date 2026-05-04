import os
import secrets
from fastapi import Header, HTTPException


def _get_api_key():
    key = os.getenv("API_KEY")
    if not key:
        key = secrets.token_urlsafe(32)
        print(f"\n[WARNING] API_KEY chua duoc cau hinh trong .env")
        print(f"  Tao key tam: {key}")
        print(f"  Them vao .env: API_KEY={key}\n")
        os.environ["API_KEY"] = key
    return key


def verify_api_key(authorization: str = Header(None)):
    api_key = _get_api_key()
    if not authorization:
        raise HTTPException(401, "Thieu header Authorization")
    if not authorization.startswith("Bearer "):
        raise HTTPException(401, "Format phai la: Bearer <API_KEY>")
    token = authorization[7:]
    if not secrets.compare_digest(token, api_key):
        raise HTTPException(401, "API key khong hop le")
