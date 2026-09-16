from fastapi import FastAPI, HTTPException, status
from src.models.legacy_input import LegacyPatientRecord
from src.transformer import map_legacy_to_eehrxf
import json

app = FastAPI(
    title="EHDS EEHRxF Clinical Gateway",
    description="Transforms legacy national clinical payloads into EEHRxF FHIR Document Bundles (IPS profile).",
    version="1.0.0"
)

@app.get("/health", status_code=status.HTTP_200_OK)
def health_check():
    return {"status": "healthy", "standard": "EHDS EEHRxF / HL7 FHIR R5"}

@app.post("/api/v1/eehrxf/patient-summary", status_code=status.HTTP_201_CREATED)
def generate_patient_summary(payload: LegacyPatientRecord):
    try:
        fhir_bundle = map_legacy_to_eehrxf(payload)
        return json.loads(fhir_bundle.model_dump_json())
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"EEHRxF transformation error: {str(e)}"
        )
