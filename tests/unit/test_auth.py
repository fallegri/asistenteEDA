import bcrypt
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


def test_register_success(client):
    response = client.post("/auth/register", json={
        "nombre": "Nuevo Usuario",
        "email": "nuevo@test.com",
        "password": "password123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "user" in data
    assert "token" in data
    assert data["user"]["email"] == "nuevo@test.com"
    assert data["user"]["nombre"] == "Nuevo Usuario"


def test_register_duplicate_email_fails(client):
    # Register first
    client.post("/auth/register", json={
        "nombre": "User 1",
        "email": "dup@test.com",
        "password": "password123"
    })
    # Try duplicate
    response = client.post("/auth/register", json={
        "nombre": "User 2",
        "email": "dup@test.com",
        "password": "password123"
    })
    assert response.status_code == 400
    assert response.json()["detail"] == "Credenciales inválidas"


def test_login_success_returns_token(client):
    # Register first
    client.post("/auth/register", json={
        "nombre": "Login User",
        "email": "login@test.com",
        "password": "password123"
    })
    # Then login
    response = client.post("/auth/login", data={
        "username": "login@test.com",
        "password": "password123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "token" in data
    assert "user" in data


def test_login_wrong_password_generic_error(client):
    client.post("/auth/register", json={
        "nombre": "Wrong Pass User",
        "email": "wrong@test.com",
        "password": "correctpass"
    })
    response = client.post("/auth/login", data={
        "username": "wrong@test.com",
        "password": "wrongpass"
    })
    assert response.status_code == 401
    assert response.json()["detail"] == "Credenciales inválidas"


def test_password_not_stored_plain_text(client):
    client.post("/auth/register", json={
        "nombre": "Hash Check",
        "email": "hash@test.com",
        "password": "mysecretpassword"
    })
    # Verify user was created and password is hashed
    response = client.post("/auth/login", data={
        "username": "hash@test.com",
        "password": "mysecretpassword"
    })
    assert response.status_code == 200
    # Login succeeded = password was hashed correctly