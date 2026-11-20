"""Run: python -m scripts.create_user USERNAME --role admin"""
import argparse
import getpass
import json
import os
from pathlib import Path
from app.security import hash_password, read_accounts

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('username')
    parser.add_argument('--role', choices=['admin','viewer'], default='viewer')
    args=parser.parse_args()
    users=read_accounts()
    if args.username in users:
        parser.error('Пользователь уже существует')
    password=getpass.getpass('Новый пароль (12+ символов, буквы и цифры): ')
    users[args.username]={'role':args.role, 'password_hash':hash_password(password)}
    path=Path(os.getenv('AUTORENT_USERS_FILE','data/users.json'))
    path.parent.mkdir(parents=True,exist_ok=True)
    with open(path,'w', opener=lambda name,flags:os.open(name,flags,0o600)) as f:
        json.dump(users,f)
    print('Пользователь создан')
if __name__=='__main__': main()
