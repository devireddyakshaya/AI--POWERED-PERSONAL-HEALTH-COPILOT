"""
FHIR R4 / ABDM-Ready Interoperability Service for MediMitra AI.
Converts extracted health data into FHIR-compliant JSON resources:
- Patient
- DiagnosticReport
- Observation
- MedicationRequest
Uses mock synthetic ABHA identifiers clearly labelled for demonstration only.
"""
from typing import Dict, Any, List
from datetime import datetime

class FHIRConverterService:
    @staticmethod
    def build_fhir_bundle(
        patient: Dict[str, Any],
        document: Dict[str, Any],
        observations: List[Dict[str, Any]],
        medications: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Creates a FHIR R4 Bundle containing Patient, DiagnosticReport,
        Observations, and MedicationRequests.
        """
        patient_id = f"pat-{patient.get('id', 1)}"
        doc_id = f"doc-{document.get('id', 1)}"
        doc_date = document.get("document_date", "2026-01-20")

        # 1. FHIR Patient Resource
        fhir_patient = {
            "resourceType": "Patient",
            "id": patient_id,
            "identifier": [
                {
                    "system": "https://healthid.ndhm.gov.in (Synthetic Demonstration Only)",
                    "value": patient.get("synthetic_abha_id", "91-4582-9012-3456 (Synthetic Demo)")
                }
            ],
            "name": [
                {
                    "use": "official",
                    "text": patient.get("full_name", "Ramesh Kumar")
                }
            ],
            "gender": (patient.get("gender") or "male").lower()
        }

        # 2. FHIR Observations
        fhir_observations = []
        obs_references = []

        for idx, obs in enumerate(observations):
            obs_id = f"obs-{doc_id}-{idx + 1}"
            obs_references.append({"reference": f"Observation/{obs_id}"})

            unit = obs.get("unit", "")
            val_num = obs.get("standardized_value")
            ref_low = obs.get("reference_range_low")
            ref_high = obs.get("reference_range_high")

            fhir_obs = {
                "resourceType": "Observation",
                "id": obs_id,
                "status": "final",
                "code": {
                    "coding": [
                        {
                            "system": "http://loinc.org",
                            "code": obs.get("standardized_code", "UNKNOWN-LOINC"),
                            "display": obs.get("test_name", "")
                        }
                    ],
                    "text": obs.get("test_name", "")
                },
                "subject": {"reference": f"Patient/{patient_id}"},
                "effectiveDateTime": f"{doc_date}T09:00:00Z",
                "interpretation": [
                    {
                        "coding": [
                            {
                                "system": "http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation",
                                "code": "H" if obs.get("interpretation") == "HIGH" else "L" if obs.get("interpretation") == "LOW" else "N",
                                "display": obs.get("interpretation", "NORMAL")
                            }
                        ]
                    }
                ]
            }

            if val_num is not None:
                fhir_obs["valueQuantity"] = {
                    "value": val_num,
                    "unit": unit,
                    "system": "http://unitsofmeasure.org"
                }

            if ref_low is not None or ref_high is not None:
                fhir_obs["referenceRange"] = [
                    {
                        "low": {"value": ref_low, "unit": unit} if ref_low is not None else None,
                        "high": {"value": ref_high, "unit": unit} if ref_high is not None else None,
                        "text": obs.get("reference_range_text", "")
                    }
                ]

            fhir_observations.append(fhir_obs)

        # 3. FHIR Medication Requests
        fhir_med_requests = []
        for idx, med in enumerate(medications):
            med_id = f"med-{doc_id}-{idx + 1}"
            fhir_med = {
                "resourceType": "MedicationRequest",
                "id": med_id,
                "status": "active",
                "intent": "order",
                "medicationCodeableConcept": {
                    "text": med.get("medicine_name", "")
                },
                "subject": {"reference": f"Patient/{patient_id}"},
                "dosageInstruction": [
                    {
                        "text": f"{med.get('dosage', '')} {med.get('frequency', '')} {med.get('timing_instructions', '')}".strip(),
                        "patientInstruction": med.get("timing_instructions", "")
                    }
                ]
            }
            fhir_med_requests.append(fhir_med)

        # 4. FHIR DiagnosticReport
        fhir_report = {
            "resourceType": "DiagnosticReport",
            "id": f"dr-{doc_id}",
            "status": "final",
            "code": {
                "coding": [
                    {
                        "system": "http://loinc.org",
                        "code": "11502-2",
                        "display": document.get("document_type", "Laboratory Report")
                    }
                ],
                "text": document.get("document_type", "Laboratory Report")
            },
            "subject": {"reference": f"Patient/{patient_id}"},
            "effectiveDateTime": f"{doc_date}T09:00:00Z",
            "issued": datetime.utcnow().isoformat() + "Z",
            "result": obs_references,
            "conclusion": "Standardized diagnostic report extraction via MediMitra AI pipeline."
        }

        # Combine into FHIR Bundle
        bundle = {
            "resourceType": "Bundle",
            "type": "collection",
            "meta": {
                "lastUpdated": datetime.utcnow().isoformat() + "Z",
                "tag": [
                    {
                        "system": "https://MediMitra.ai/tags",
                        "code": "SYNTHETIC_DEMO",
                        "display": "Synthetic ABDM/FHIR Demonstration Payload"
                    }
                ]
            },
            "entry": [
                {"resource": fhir_patient},
                {"resource": fhir_report}
            ] + [{"resource": obs} for obs in fhir_observations] + [{"resource": med} for med in fhir_med_requests]
        }

        return bundle
