import pytest
import mongomock
from unittest.mock import patch
from app.main import create_app


@pytest.fixture
def client():
    with patch("app.main.MongoClient", new=mongomock.MongoClient):
        app = create_app()
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client


def test_home_page(client):
    response = client.get("/")
    assert response.status_code == 200


def test_admin_dashboard(client):
    response = client.get("/admin-dashboard")
    assert response.status_code == 200


def test_student_dashboard(client):
    response = client.get(
        "/student-dashboard?_rfidTag=123&_name=John&_rollNo=21CS001&_department=CSE")
    assert response.status_code == 200
    assert b"John" in response.data or b"21CS001" in response.data


def test_generate_attendance_no_input(client):
    response = client.post("/api/generate-attendance", json={})
    assert response.status_code == 400
    assert response.get_json()["error"] == "No data received"




def test_receive_rfid_missing(client):
    response = client.post("/receive-rfid", json={})
    assert response.status_code == 200
    assert "rfid" in response.get_json()
