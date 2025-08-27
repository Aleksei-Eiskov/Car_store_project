from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)

def test_health():
    r = client.get('/health')
    assert r.status_code == 200
    assert r.json()['status'] == 'ok'

def test_crud_brand_and_car():
    # create brand
    r = client.post('/brands', json={'name': 'Audi'})
    assert r.status_code == 201
    brand = r.json()
    # list brands
    r = client.get('/brands')
    assert r.status_code == 200
    assert any(b['name'] == 'Audi' for b in r.json())
    # create car
    r = client.post('/cars', json={'name': 'A4', 'price': 35000, 'brand_id': brand['id']})
    assert r.status_code == 201
    car = r.json()
    # get car
    r = client.get(f"/cars/{car['id']}")
    assert r.status_code == 200
    # patch car
    r = client.patch(f"/cars/{car['id']}", json={'price': 36000})
    assert r.status_code == 200
    assert r.json()['price'] == 36000
    # filters
    r = client.get('/cars', params={'q': 'a4', 'min_price': 30000, 'max_price': 40000})
    assert r.status_code == 200
    assert any(c['name'] == 'A4' for c in r.json())
    # delete
    r = client.delete(f"/cars/{car['id']}")
    assert r.status_code == 204
