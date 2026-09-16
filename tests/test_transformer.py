from datetime import date
from src.models.legacy_input import LegacyPatientRecord, LegacyCondition, LegacyMedication
from src.transformer import map_legacy_to_eehrxf
from fhir.resources.composition import Composition
from fhir.resources.patient import Patient
from fhir.resources.condition import Condition
from fhir.resources.medicationstatement import MedicationStatement

def test_eehrxf_document_bundle_structure():
    record = LegacyPatientRecord(
        national_id="ES-X1234567Y",
        country_code="ES",
        given_name="Carlos",
        family_name="García",
        birth_date=date(1975, 11, 20),
        gender="male",
        conditions=[
            LegacyCondition(code="I10", display="Essential (primary) hypertension")
        ],
        medications=[
            LegacyMedication(name="Amlodipine", dose="5mg once daily", atc_code="C08CA01")
        ]
    )

    bundle = map_legacy_to_eehrxf(record)

    # 1. Document Bundle Integrity
    assert bundle.type == "document"
    assert len(bundle.entry) == 4

    # 2. First resource MUST be Composition (IPS requirement)
    first_entry = bundle.entry[0].resource
    assert isinstance(first_entry, Composition)
    assert first_entry.type.coding[0].system == "http://loinc.org"
    assert first_entry.type.coding[0].code == "60591-5"

    # 3. Patient identity and ISO country namespace
    patient_entry = bundle.entry[1].resource
    assert isinstance(patient_entry, Patient)
    assert patient_entry.identifier[0].system == "urn:oid:iso:3166-1:ES"
    assert patient_entry.identifier[0].value == "ES-X1234567Y"

    # 4. Clinical entries conformance
    condition_entry = bundle.entry[2].resource
    assert isinstance(condition_entry, Condition)
    assert condition_entry.code.coding[0].system == "http://hl7.org/fhir/sid/icd-10"
    assert condition_entry.code.coding[0].code == "I10"

    medication_entry = bundle.entry[3].resource
    assert isinstance(medication_entry, MedicationStatement)
    assert medication_entry.status == "active"
    assert medication_entry.medication.concept.coding[0].system == "http://www.whocc.no/atc"
    assert medication_entry.medication.concept.coding[0].code == "C08CA01"
