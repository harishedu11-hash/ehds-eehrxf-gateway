from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_health_check_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_generate_patient_summary_valid():
    payload = {
        "national_id": "FR-987654321",
        "country_code": "FR",
        "given_name": "Jean",
        "family_name": "Dupont",
        "birth_date": "1980-03-15",
        "gender": "male",
        "conditions": [
            {"code": "E10.9", "display": "Type 1 diabetes mellitus"}
        ],
        "medications": [
            {"name": "Insulin Lispro", "dose": "10 units before meals", "atc_code": "A10AB04"}
        ]
    }
    response = client.post("/api/v1/eehrxf/patient-summary", json=payload)
    assert response.status_code == 201
    
    data = response.json()
    assert data["resourceType"] == "Bundle"
    assert data["type"] == "document"
    assert len(data["entry"]) == 4

def test_generate_patient_summary_invalid_country():
    # ISO country code requires strictly 2 characters
    invalid_payload = {
        "national_id": "FR-987654321",
        "country_code": "FRANCE",
        "given_name": "Jean",
        "family_name": "Dupont",
        "birth_date": "1980-03-15",
        "gender": "male"
    }
    response = client.post("/api/v1/eehrxf/patient-summary", json=invalid_payload)
    assert response.status_code == 422
