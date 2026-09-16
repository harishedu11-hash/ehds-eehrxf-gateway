import uuid
from datetime import datetime, timezone
from fhir.resources.bundle import Bundle, BundleEntry
from fhir.resources.composition import Composition, CompositionSection
from fhir.resources.patient import Patient
from fhir.resources.humanname import HumanName
from fhir.resources.condition import Condition
from fhir.resources.medicationstatement import MedicationStatement
from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.codeablereference import CodeableReference
from fhir.resources.coding import Coding
from fhir.resources.reference import Reference
from fhir.resources.identifier import Identifier
from src.models.legacy_input import LegacyPatientRecord

def map_legacy_to_eehrxf(record: LegacyPatientRecord) -> Bundle:
    bundle_id = str(uuid.uuid4())
    patient_id = f"urn:uuid:{uuid.uuid4()}"
    now_iso = datetime.now(timezone.utc)

    # 1. Map Demographic details to FHIR Patient with typed HumanName
    patient = Patient.model_construct(
        id=patient_id.replace("urn:uuid:", ""),
        identifier=[
            Identifier.model_construct(
                system=f"urn:oid:iso:3166-1:{record.country_code}",
                value=record.national_id
            )
        ],
        name=[
            HumanName.model_construct(
                family=record.family_name,
                given=[record.given_name]
            )
        ],
        birthDate=record.birth_date.isoformat(),
        gender=record.gender.lower()
    )

    entries = [BundleEntry.model_construct(fullUrl=patient_id, resource=patient)]
    condition_refs = []
    medication_refs = []

    # 2. Map Active Conditions
    for cond in record.conditions:
        cond_id = f"urn:uuid:{uuid.uuid4()}"
        fhir_cond = Condition.model_construct(
            id=cond_id.replace("urn:uuid:", ""),
            subject=Reference.model_construct(reference=patient_id),
            code=CodeableConcept.model_construct(
                coding=[
                    Coding.model_construct(
                        system="http://hl7.org/fhir/sid/icd-10",
                        code=cond.code,
                        display=cond.display
                    )
                ],
                text=cond.display
            )
        )
        if cond.onset_date:
            fhir_cond.onsetDateTime = cond.onset_date.isoformat()

        entries.append(BundleEntry.model_construct(fullUrl=cond_id, resource=fhir_cond))
        condition_refs.append(Reference.model_construct(reference=cond_id))

    # 3. Map Active Medications
    for med in record.medications:
        med_id = f"urn:uuid:{uuid.uuid4()}"
        coding_list = []
        if med.atc_code:
            coding_list.append(
                Coding.model_construct(
                    system="http://www.whocc.no/atc",
                    code=med.atc_code,
                    display=med.name
                )
            )

        med_concept = CodeableConcept.model_construct(
            coding=coding_list,
            text=f"{med.name} ({med.dose})"
        )

        fhir_med = MedicationStatement.model_construct(
            id=med_id.replace("urn:uuid:", ""),
            status="active",
            subject=Reference.model_construct(reference=patient_id),
            medication=CodeableReference.model_construct(concept=med_concept)
        )
        entries.append(BundleEntry.model_construct(fullUrl=med_id, resource=fhir_med))
        medication_refs.append(Reference.model_construct(reference=med_id))

    # 4. Construct Composition Header (IPS Document Header)
    comp_id = f"urn:uuid:{uuid.uuid4()}"
    sections = []
    if condition_refs:
        sections.append(
            CompositionSection.model_construct(
                title="Active Problems and Diagnoses",
                entry=condition_refs
            )
        )
    if medication_refs:
        sections.append(
            CompositionSection.model_construct(
                title="Current Medications",
                entry=medication_refs
            )
        )

    composition = Composition.model_construct(
        id=comp_id.replace("urn:uuid:", ""),
        status="final",
        type=CodeableConcept.model_construct(
            coding=[
                Coding.model_construct(
                    system="http://loinc.org",
                    code="60591-5",
                    display="Patient Summary Document"
                )
            ]
        ),
        subject=Reference.model_construct(reference=patient_id),
        date=now_iso,
        author=[Reference.model_construct(display="National Clinical Gateway Adapter")],
        title="EEHRxF Patient Summary",
        section=sections
    )

    entries.insert(0, BundleEntry.model_construct(fullUrl=comp_id, resource=composition))

    return Bundle.model_construct(
        id=bundle_id,
        type="document",
        timestamp=now_iso,
        entry=entries
    )
