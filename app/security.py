"""Local teaching authentication. Use HTTPS when deployed outside localhost."""
import hashlib
import json
import os
import secrets
from pathlib import Path
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials

basic = HTTPBasic(auto_error=False)

def hash_password(password, salt=None):
    if len(password) < 12 or not any(c.isalpha() for c in password) or not any(c.isdigit() for c in password):
        raise ValueError("Пароль: минимум 12 символов, буквы и цифры")
    salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac('sha256', password.encode(), bytes.fromhex(salt), 200000).hex()
    return salt + ':' + digest

def read_accounts():
    path = Path(os.getenv('AUTORENT_USERS_FILE', 'data/users.json'))
    if not path.exists():
        return {}
    return json.loads(path.read_text())

DUMMY_HASH = hash_password(secrets.token_urlsafe(24) + '1')

def require_user(credentials: HTTPBasicCredentials = Depends(basic)):
    accounts = read_accounts()
    account = accounts.get(credentials.username) if credentials else None
    stored = account['password_hash'] if account else DUMMY_HASH
    salt, expected = stored.split(':')
    password = credentials.password if credentials else ''
    actual = hashlib.pbkdf2_hmac('sha256', password.encode(), bytes.fromhex(salt), 200000).hex()
    if not secrets.compare_digest(actual, expected) or not account:
        raise HTTPException(401, 'Неверные учётные данные', headers={'WWW-Authenticate':'Basic'})
    return {'username': credentials.username, 'role': account['role']}

def require_admin(user=Depends(require_user)):
    if user['role'] != 'admin':
        raise HTTPException(403, 'Недостаточно прав')
    return user
