import pytest
from sqlalchemy import event
from sqlmodel import SQLModel, Session, create_engine
from fastapi.testclient import TestClient
from app.main import app
from app.database.db import get_session

@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr("app.main.init_db", lambda: None)
    engine = create_engine(f"sqlite:///{tmp_path}/test.db", connect_args={"check_same_thread":False})
    @event.listens_for(engine, "connect")
    def fk(conn, _):
        conn.execute("PRAGMA foreign_keys=ON")
    SQLModel.metadata.create_all(engine)
    def session():
        with Session(engine) as s: yield s
    app.dependency_overrides[get_session] = session
    with TestClient(app) as c: yield c
    app.dependency_overrides.clear()
    engine.dispose()

def setup_data(c):
    cat = c.post('/categories', json={'name':'Comfort','daily_rate':20000}).json()
    car = c.post('/cars', json={'brand':'Toyota','model':'Camry','plate':'TEST-01','category_id':cat['id']}).json()
    person = c.post('/clients', json={'full_name':'Test Client','license_number':'TEST-L'}).json()
    return cat, car, person

def test_crud_and_filter(client):
    assert client.get('/').status_code == 200
    assert client.get('/cars').json() == []
    cat, car, person = setup_data(client)
    assert client.get('/cars',params={'search':'Cam','min_price':19000,'max_price':21000}).json()[0]['id'] == car['id']
    assert client.get('/cars',params={'search':"' OR 1=1 --"}).json() == []
    assert client.get('/cars',params={'search':'%'}).json() == []
    r = client.patch('/cars/'+str(car['id']),json={'model':'Corolla'})
    assert r.status_code == 200 and r.json()['brand']=='Toyota' and r.json()['model']=='Corolla'
    assert client.delete('/categories/'+str(cat['id'])).status_code == 409
    assert client.delete('/cars/'+str(car['id'])).status_code == 204
    assert client.get('/cars/'+str(car['id'])).status_code == 404
    assert client.patch('/cars/'+str(car['id']),json={'model':'x'}).status_code == 404
    assert client.delete('/categories/'+str(cat['id'])).status_code == 204

@pytest.mark.parametrize('payload',[{'name':'','daily_rate':1},{'name':'x','daily_rate':0},{'name':'x','daily_rate':-1}])
def test_validation(client,payload):
    assert client.post('/categories',json=payload).status_code==422

def test_null_duplicate_and_foreign_key(client):
    cat,car,person=setup_data(client)
    assert client.post('/categories',json={'name':'Comfort','daily_rate':1}).status_code==409
    assert client.patch('/categories/'+str(cat['id']),json={'name':None}).status_code==422
    assert client.patch('/categories/'+str(cat['id']),json={'daily_rate':-1}).status_code==422
    assert client.post('/cars',json={'brand':'x','model':'x','plate':'x','category_id':999}).status_code==422
    assert client.get('/cars',params={'min_price':20,'max_price':10}).status_code==422
    assert client.delete('/clients/999').status_code==404

def test_rental_dates_overlap_and_history(client):
    cat,car,person=setup_data(client)
    payload={'car_id':car['id'],'client_id':person['id'],'start_date':'2026-11-10','end_date':'2026-11-12','daily_rate':20000}
    r=client.post('/rentals',json=payload)
    assert r.status_code==201
    assert client.post('/rentals',json=payload).status_code==409
    assert client.post('/rentals',json={**payload,'end_date':'2026-11-09'}).status_code==422
    assert client.delete('/clients/'+str(person['id'])).status_code==409
    assert client.patch('/categories/'+str(cat['id']),json={'daily_rate':30000}).status_code==200
    assert client.get('/rentals/'+str(r.json()['id'])).json()['daily_rate']==20000
    assert client.post('/rentals',json={**payload,'start_date':'2026-11-12','end_date':'2026-11-13'}).status_code==201
    assert client.patch('/rentals/'+str(r.json()['id']),json={'end_date':'2026-11-13'}).status_code==409
