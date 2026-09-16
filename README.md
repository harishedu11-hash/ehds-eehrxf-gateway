# EHDS EEHRxF Cross-Border Clinical Gateway

[![FHIR R5](https://img.shields.io/badge/FHIR-R5-blue.svg)](https://hl7.org/fhir/)
[![EHDS Compliant](https://img.shields.io/badge/EHDS-Chapter%20II%20%2F%20Art.%2014-green.svg)](https://health.ec.europa.eu/ehealth-digital-health-and-care/european-health-data-space_en)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)](tests/)

A reference implementation of a **National Contact Point for eHealth (NCPeH)** adapter conforming to the **European Electronic Health Record Exchange Format (EEHRxF)** mandated by the European Health Data Space (EHDS) Regulation.

---

## 1. Regulatory Context & Legal Basis

- **EHDS Regulation Chapter II (Primary Use of Electronic Health Data):** Enables cross-border patient mobility and guarantees citizen rights to clinical data portability.
- **Article 14 Priority Category - Patient Summary:** Mandates that healthcare providers across EU Member States must be able to export and import standardized patient summaries to support unscheduled care abroad (MyHealth@EU).
- **International Patient Summary (IPS):** Technical alignment with HL7 Europe Implementation Guides and ISO 27269 standards.

---

## 2. Architecture & Data Flow

[ National Hospital EHR ]
│
▼  (Legacy JSON / Relational Payload)
[ Ingestion Gateway: FastAPI ] ──► (Input Validation & Country Namespace Check)
│
▼  (FHIR R5 / IPS Transformation Engine)
[ EEHRxF FHIR Bundle (type="document") ]
├── Composition (LOINC 60591-5: Patient Summary Document)
├── Patient (ISO 3166-1 National Citizen Namespace)
├── Condition (ICD-10 / SNOMED-CT Coded Active Diagnoses)
└── MedicationStatement (WHO ATC Classification)
│
▼
[ MyHealth@EU Cross-Border Service Interface / NCPeH ]


---

## 3. Clinical Coding Standards Applied

| Domain | Coding System | Standard URI / OID |
| :--- | :--- | :--- |
| **Document Architecture** | LOINC | `http://loinc.org` (`60591-5`) |
| **Active Conditions** | ICD-10 | `http://hl7.org/fhir/sid/icd-10` |
| **Medication Therapies** | WHO ATC | `http://www.whocc.no/atc` |
| **Jurisdictional Identity** | ISO 3166-1 | `urn:oid:iso:3166-1:{COUNTRY_CODE}` |

---

## 4. Quickstart & Verification

### Local Setup
```bash
# 1. Clone the repository
git clone [https://github.com/harishedu11-hash/ehds-eehrxf-gateway.git](https://github.com/harishedu11-hash/ehds-eehrxf-gateway.git)
cd ehds-eehrxf-gateway

# 2. Set up environment
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 3. Run conformance test suite
pytest

# 4. Run the cross-border demo pipeline
python3 -m src.demo
Running the API Gateway
Bash
uvicorn src.main:app --reload --port 8000
Interactive API docs available at: http://localhost:8000/docs

Containerized Execution
Bash
docker build -t ehds-eehrxf-gateway:latest .
docker run -p 8000:8000 ehds-eehrxf-gateway:latest
5. Repository Structure
Plaintext
├── src/
│   ├── models/
│   │   └── legacy_input.py    # Ingestion schema with Pydantic validation
│   ├── transformer.py         # FHIR R5 EEHRxF IPS Document Bundle generator
│   ├── main.py                # RESTful FastAPI microservice endpoint
│   └── demo.py                # End-to-end clinical demonstration script
├── tests/
│   ├── test_transformer.py    # FHIR structural conformance test suite
│   └── test_api.py            # HTTP contract & boundary condition tests
├── Dockerfile                 # Container packaging
├── pyproject.toml             # Pytest runtime configuration
└── requirements.txt           # Python dependency tree
