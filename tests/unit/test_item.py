from fastapi.testclient import TestClient


def test_create_item_returns_201(client, auth_headers):
    # Limpiar items existentes
    items_resp = client.get("/items/", headers=auth_headers)
    for item in items_resp.json():
        client.delete(f"/items/{item['id']}", headers=auth_headers)
    
    response = client.post("/items/", json={
        "nombre": "Item Test",
        "descripcion": "Descripción de prueba",
        "estado": "active"
    }, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["nombre"] == "Item Test"


def test_create_item_returns_id(client, auth_headers):
    # Limpiar
    items_resp = client.get("/items/", headers=auth_headers)
    for item in items_resp.json():
        client.delete(f"/items/{item['id']}", headers=auth_headers)
    
    response = client.post("/items/", json={
        "nombre": "Another Item",
        "descripcion": "Desc",
        "estado": "active"
    }, headers=auth_headers)
    assert response.status_code == 201
    assert isinstance(response.json()["id"], int)


def test_list_empty_returns_empty(client, auth_headers):
    # Limpiar
    items_resp = client.get("/items/", headers=auth_headers)
    for item in items_resp.json():
        client.delete(f"/items/{item['id']}", headers=auth_headers)
    
    response = client.get("/items/", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == []


def test_list_after_create_has_items(client, auth_headers):
    # Limpiar
    items_resp = client.get("/items/", headers=auth_headers)
    for item in items_resp.json():
        client.delete(f"/items/{item['id']}", headers=auth_headers)
    
    client.post("/items/", json={"nombre": "Item 1", "descripcion": "", "estado": "active"}, headers=auth_headers)
    client.post("/items/", json={"nombre": "Item 2", "descripcion": "", "estado": "active"}, headers=auth_headers)
    response = client.get("/items/", headers=auth_headers)
    assert response.status_code == 200
    items = response.json()
    assert len(items) == 2
    assert items[0]["nombre"] == "Item 1"
    assert items[1]["nombre"] == "Item 2"


def test_get_existing_returns_200(client, auth_headers):
    # Limpiar
    items_resp = client.get("/items/", headers=auth_headers)
    for item in items_resp.json():
        client.delete(f"/items/{item['id']}", headers=auth_headers)
    
    create_resp = client.post("/items/", json={"nombre": "Get Me", "descripcion": "", "estado": "active"}, headers=auth_headers)
    item_id = create_resp.json()["id"]
    response = client.get(f"/items/{item_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["id"] == item_id


def test_get_nonexistent_returns_404(client, auth_headers):
    # Limpiar
    items_resp = client.get("/items/", headers=auth_headers)
    for item in items_resp.json():
        client.delete(f"/items/{item['id']}", headers=auth_headers)
    
    response = client.get("/items/999999", headers=auth_headers)
    assert response.status_code == 404


def test_delete_returns_204(client, auth_headers):
    # Limpiar
    items_resp = client.get("/items/", headers=auth_headers)
    for item in items_resp.json():
        client.delete(f"/items/{item['id']}", headers=auth_headers)
    
    create_resp = client.post("/items/", json={"nombre": "To Delete", "descripcion": "", "estado": "active"}, headers=auth_headers)
    item_id = create_resp.json()["id"]
    response = client.delete(f"/items/{item_id}", headers=auth_headers)
    assert response.status_code == 204


def test_deleted_not_in_list(client, auth_headers):
    # Limpiar
    items_resp = client.get("/items/", headers=auth_headers)
    for item in items_resp.json():
        client.delete(f"/items/{item['id']}", headers=auth_headers)
    
    create_resp = client.post("/items/", json={"nombre": "Will Delete", "descripcion": "", "estado": "active"}, headers=auth_headers)
    item_id = create_resp.json()["id"]
    client.delete(f"/items/{item_id}", headers=auth_headers)
    response = client.get("/items/", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) == 0


def test_create_without_auth_returns_401(client):
    response = client.post("/items/", json={"nombre": "No Auth", "descripcion": "", "estado": "active"})
    assert response.status_code == 401


def test_get_without_auth_returns_401(client):
    response = client.get("/items/1")
    assert response.status_code == 401


def test_update_item(client, auth_headers):
    # Limpiar
    items_resp = client.get("/items/", headers=auth_headers)
    for item in items_resp.json():
        client.delete(f"/items/{item['id']}", headers=auth_headers)
    
    create_resp = client.post("/items/", json={"nombre": "Original", "descripcion": "", "estado": "active"}, headers=auth_headers)
    item_id = create_resp.json()["id"]
    response = client.patch(f"/items/{item_id}", json={"nombre": "Actualizado"}, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["nombre"] == "Actualizado"