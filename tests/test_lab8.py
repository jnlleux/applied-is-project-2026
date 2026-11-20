import json
import logging
import pytest
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select
from app.main import app
from app.database.models import Category
from app.database.db import get_session
from app.security import hash_password, require_user
from test_api import client

@pytest.fixture
def secured(client, tmp_path, monkeypatch):
    password='TestingPassword123!'
    path=tmp_path/'users.json'
    path.write_text(json.dumps({u:{'role':r,'password_hash':hash_password(password)} for u,r in [('admin','admin'),('reader','viewer')]}))
    monkeypatch.setenv('AUTORENT_USERS_FILE', str(path))
    app.dependency_overrides.pop(require_user)
    return client, password

def test_full_put_crud(client):
    result=client.post('/categories',json={'name':'Integration','daily_rate':100})
    assert result.status_code==201
    key=result.json()['id']
    assert client.get(f'/categories/{key}').json()['name']=='Integration'
    assert client.put(f'/categories/{key}',json={'name':'Updated','daily_rate':200}).status_code==200
    assert client.get(f'/categories/{key}').json()['daily_rate']==200
    assert client.delete(f'/categories/{key}').status_code==204
    assert client.get(f'/categories/{key}').status_code==404

def test_put_requires_all_fields(client):
    assert client.put('/categories/1',json={'name':'missing price'}).status_code==422

def test_database_rollback(client):
    with next(app.dependency_overrides[get_session]()) as session:
        before=list(session.exec(select(Category)).all())
        session.add(Category(name='must rollback', daily_rate=100))
        session.add(Category(name='invalid', daily_rate=None))
        with pytest.raises(IntegrityError): session.commit()
        session.rollback()
        assert list(session.exec(select(Category)).all())==before
        session.add(Category(name='after rollback',daily_rate=1));session.commit()
    assert client.get('/categories').json()[0]['name']=='after rollback'

def test_empty_json(client):
    assert client.post('/categories',json={}).status_code==422

def test_malformed_json(client):
    assert client.post('/categories',content='{broken',headers={'Content-Type':'application/json'}).status_code==400

def test_missing_client(client):
    assert client.get('/clients/99999').status_code==404

def test_no_auth(secured):
    c,_=secured
    assert c.get('/clients').status_code==401
    assert c.post('/categories',json={'name':'x','daily_rate':1}).status_code==401

def test_wrong_login(secured):
    c,p=secured
    assert c.get('/auth/me',auth=('missing',p)).status_code==401

def test_empty_password(secured):
    c,_=secured
    assert c.get('/auth/me',auth=('admin','')).status_code==401

@pytest.mark.parametrize('password',['','123','allletterslong','123456789012'])
def test_weak_password(password):
    with pytest.raises(ValueError): hash_password(password)

def test_role_limits(secured):
    c,p=secured
    assert c.get('/clients',auth=('reader',p)).status_code==200
    assert c.post('/categories',json={'name':'denied','daily_rate':1},auth=('reader',p)).status_code==403
    assert c.post('/categories',json={'name':'allowed','daily_rate':1},auth=('admin',p)).status_code==201

def test_secrets_not_in_errors_or_logs(secured,caplog):
    c,p=secured
    with caplog.at_level(logging.INFO):
        result=c.get('/auth/me',auth=('admin',p+'wrong'))
        bad=c.post('/categories',json={'name':p,'daily_rate':-1},auth=('admin',p))
    assert result.status_code==401 and bad.status_code==422
    assert p not in result.text+bad.text+caplog.text
    assert 'password_hash' not in result.text

def test_public_showroom_catalog(secured):
    c,_=secured
    assert c.get('/cars').status_code==200
    assert c.get('/categories').status_code==200
    assert c.get('/showroom/').status_code==200
