import json
from datetime import date
from src.models.legacy_input import LegacyPatientRecord, LegacyCondition, LegacyMedication
from src.transformer import map_legacy_to_eehrxf

def run_cross_border_demo():
    print("=" * 70)
    print("EHDS EEHRxF Cross-Border Exchange Demonstration (Chapter II)")
    print("=" * 70)

    # 1. Simulate incoming legacy electronic health record from a local hospital
    print("\n[1] Ingesting raw national EHR payload...")
    patient_record = LegacyPatientRecord(
        national_id="NL-B78945612",
        country_code="NL",
        given_name="Lars",
        family_name="van der Meer",
        birth_date=date(1968, 8, 22),
        gender="male",
        conditions=[
            LegacyCondition(
                code="I25.10",
                display="Atherosclerotic heart disease of native coronary artery",
                onset_date=date(2019, 4, 10)
            ),
            LegacyCondition(
                code="E78.0",
                display="Pure hypercholesterolemia",
                onset_date=date(2020, 1, 15)
            )
        ],
        medications=[
            LegacyMedication(
                name="Atorvastatin",
                dose="20mg once daily at bedtime",
                atc_code="C10AA05"
            ),
            LegacyMedication(
                name="Aspirin Cardio",
                dose="100mg once daily",
                atc_code="B01AC06"
            )
        ]
    )
    print(f"    Patient: {patient_record.given_name} {patient_record.family_name} (DOB: {patient_record.birth_date})")
    print(f"    Identifier: {patient_record.national_id} [Country: {patient_record.country_code}]")
    print(f"    Active Conditions: {len(patient_record.conditions)} | Active Medications: {len(patient_record.medications)}")

    # 2. Transform into EEHRxF Document Bundle
    print("\n[2] Executing EEHRxF / HL7 FHIR Transformer...")
    bundle = map_legacy_to_eehrxf(patient_record)
    bundle_json = json.loads(bundle.model_dump_json())

    # 3. Output structural verification
    print("\n[3] Generated Standardized EEHRxF Document Bundle:")
    print(f"    - Bundle ID: {bundle_json.get('id')}")
    print(f"    - Bundle Type: {bundle_json.get('type')}")
    print(f"    - Document Timestamp: {bundle_json.get('timestamp')}")
    print(f"    - Total Bundled Entries: {len(bundle_json.get('entry', []))}")

    # Inspect the composition sections
    composition = bundle_json["entry"][0]["resource"]
    print(f"\n[4] Lead Resource: {composition.get('resourceType')} ({composition.get('title')})")
    print(f"    - Document Code: LOINC {composition['type']['coding'][0]['code']} ({composition['type']['coding'][0]['display']})")
    print(f"    - Sections created: {len(composition.get('section', []))}")
    for sec in composition.get("section", []):
        print(f"      * {sec.get('title')} -> References: {[e.get('reference') for e in sec.get('entry', [])]}")

    print("\n" + "=" * 70)
    print("Conforms to EHDS Article 14 Priority Category: Patient Summary")
    print("=" * 70)

if __name__ == "__main__":
    run_cross_border_demo()
