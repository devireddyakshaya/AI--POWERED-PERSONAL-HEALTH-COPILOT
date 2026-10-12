"""
AI Health Explainer integration for MediMitra AI.
Uses Google Gemini API when configured, with high-fidelity deterministic
DEMO MODE fallback when running offline or without API keys.
Strictly adheres to medical safety rules (no independent diagnoses, informational disclaimer).
"""
import json
import logging
from typing import Dict, Any, List
from backend.app.config import GEMINI_API_KEY, is_demo_mode
from backend.app.services.telugu_service import TeluguHealthTranslator

logger = logging.getLogger(__name__)

GEMINI_CLIENT = None
if GEMINI_API_KEY and GEMINI_API_KEY != "your_gemini_api_key_here":
    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        GEMINI_CLIENT = genai
    except Exception as e:
        logger.warning(f"Could not initialize Google Generative AI client: {e}")
        GEMINI_CLIENT = None


SYSTEM_PROMPT = """
You are MediMitra AI — an empathetic, medically safe Health Copilot.
You help patients understand their laboratory reports and prescriptions.

STRICT MEDICAL SAFETY RULES:
1. INFORMATIONAL ONLY: This summary is not a substitute for professional clinical judgment.
2. NEVER DIAGNOSE: Do not say 'You have diabetes/hypertension/chronic kidney disease'. Say 'The test result is outside the laboratory's reference range and requires clinical correlation by your doctor.'
3. NEVER PRESCRIBE OR CHANGE DOSES: Do not recommend medications, lifestyle alterations as definitive cures, or changing dosages.
4. USE REFERENCE RANGES: Interpret values strictly against the reference ranges provided in the report. Explain that reference ranges can vary between different laboratories.
5. EXPLAIN MEDICAL TERMS: Demystify tests (like HbA1c, Triglycerides, Creatinine) in simple everyday English.
6. TELUGU EXPLANATION: Generate an accompanying explanation in natural, polite Telugu (తెలుగు). Strictly keep medicine names, numbers, units, and dates in original form.
7. EVIDENCE LINKING: Link key findings directly to extracted facts and evidence excerpts.

Return a valid JSON object matching this schema:
{
  "english_summary": "Friendly patient summary in plain English...",
  "telugu_summary": "Natural Telugu summary preserving numbers and medicine names...",
  "key_findings": [
    {
      "title": "Fasting Blood Glucose",
      "finding": "Measured at 142 mg/dL, which is above the laboratory's normal range of 70 - 99 mg/dL.",
      "interpretation": "ABNORMAL_HIGH",
      "evidence_excerpt": "Fasting Blood Glucose 142 mg/dL (Ref: 70 - 99)",
      "reference_range": "70 - 99 mg/dL",
      "needs_verification": false
    }
  ],
  "questions_for_doctor": [
    "My fasting blood glucose is 142 mg/dL. What follow-up checks or lifestyle guidelines do you advise?",
    "Should we repeat this test or evaluate HbA1c to assess longer-term trends?"
  ],
  "uncertainty_notes": "Note: Reference ranges depend on specific laboratory assays, age, and individual patient context. Please share this report with your physician."
}
"""


class AIService:
    @staticmethod
    def generate_health_summary(
        patient_name: str,
        document_type: str,
        document_date: str,
        observations: List[Dict[str, Any]],
        medications: List[Dict[str, Any]],
        raw_text: str = ""
    ) -> Dict[str, Any]:
        """
        Generates structured medical explanations in English & Telugu with evidence linking.
        Falls back seamlessly to high-fidelity synthetic engine in Demo Mode.
        """
        if not is_demo_mode() and GEMINI_CLIENT is not None:
            try:
                return AIService._call_gemini_api(patient_name, document_type, document_date, observations, medications, raw_text)
            except Exception as e:
                logger.error(f"Gemini API call failed, switching to deterministic fallback: {e}")

        # Deterministic Demo Mode engine
        return AIService._generate_deterministic_summary(patient_name, document_type, document_date, observations, medications)

    @staticmethod
    def _call_gemini_api(
        patient_name: str,
        document_type: str,
        document_date: str,
        observations: List[Dict[str, Any]],
        medications: List[Dict[str, Any]],
        raw_text: str
    ) -> Dict[str, Any]:
        """Invokes Gemini 1.5/2.0 model with structured prompting."""
        model = GEMINI_CLIENT.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config={"response_mime_type": "application/json"}
        )

        user_prompt = f"""
Patient Name: {patient_name}
Document Type: {document_type}
Document Date: {document_date}

EXTRACTED OBSERVATIONS:
{json.dumps(observations, indent=2)}

EXTRACTED MEDICATIONS:
{json.dumps(medications, indent=2)}

SOURCE TEXT EXCERPT:
{raw_text[:2000]}

Generate the structured JSON response following the system instructions.
"""
        response = model.generate_content([SYSTEM_PROMPT, user_prompt])
        parsed = json.loads(response.text)
        parsed["is_demo_generated"] = False
        return parsed

    @staticmethod
    def _generate_deterministic_summary(
        patient_name: str,
        document_type: str,
        document_date: str,
        observations: List[Dict[str, Any]],
        medications: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        High-fidelity deterministic medical explanation engine for Demo Mode.
        Guarantees accurate, evidence-linked summaries without requiring external API keys.
        """
        abnormal_obs = [o for o in observations if o.get("interpretation") in ("HIGH", "LOW")]
        normal_obs = [o for o in observations if o.get("interpretation") == "NORMAL"]

        key_findings = []
        questions_for_doctor = []

        # Build key findings
        for obs in observations:
            interp = obs.get("interpretation", "UNCERTAIN")
            t_name = obs.get("test_name", "")
            val = obs.get("original_value", "")
            unit = obs.get("unit", "")
            ref = obs.get("reference_range_text", "Not specified")
            excerpt = obs.get("evidence_excerpt", f"{t_name} {val} {unit}")

            status_desc = "within the expected reference range"
            finding_interp = "NORMAL"

            if interp == "HIGH":
                status_desc = f"above the standard reference range ({ref})"
                finding_interp = "ABNORMAL_HIGH"
                questions_for_doctor.append(f"My {t_name} is elevated at {val} {unit} (reference: {ref}). What further evaluation or management do you suggest?")
            elif interp == "LOW":
                status_desc = f"below the standard reference range ({ref})"
                finding_interp = "ABNORMAL_LOW"
                questions_for_doctor.append(f"My {t_name} is lower than expected at {val} {unit} (reference: {ref}). Should we evaluate potential causes?")

            key_findings.append({
                "title": t_name,
                "finding": f"Measured at {val} {unit}, which is {status_desc}.",
                "interpretation": finding_interp,
                "evidence_excerpt": excerpt,
                "reference_range": ref,
                "needs_verification": obs.get("confidence_score", 1.0) < 0.85
            })

        # Explain medical terms in English
        eng_parts = []
        date_text = f" dated {document_date}" if document_date else ""
        eng_parts.append(
            f"Hello {patient_name}, here is an easy-to-understand breakdown of your {document_type}"
            f"{date_text}. This report contains {len(observations)} laboratory test results."
        )

        if abnormal_obs:
            eng_parts.append("\nKey Findings Requiring Attention:")
            for ab in abnormal_obs:
                eng_parts.append(
                    f"• {ab['test_name']}: Your level is {ab['original_value']} {ab['unit']}, which is higher than "
                    f"the reference interval provided ({ab['reference_range_text']}). "
                    f"This indicates a value outside normal laboratory limits that your clinician will evaluate."
                )

        if normal_obs:
            normal_names = [f"{o['test_name']} ({o['original_value']} {o['unit']})" for o in normal_obs]
            eng_parts.append(
                f"\nNormal Findings: {', '.join(normal_names)} are all within standard laboratory reference ranges."
            )

        if medications:
            eng_parts.append("\nPrescriptions Recorded:")
            for med in medications:
                eng_parts.append(
                    f"• {med['medicine_name']} ({med.get('dosage', 'Prescribed strength')}): "
                    f"{med.get('frequency', '')} - {med.get('timing_instructions', '')}."
                )

        eng_parts.append(
            "\nNote: Test results must always be interpreted in the context of your complete medical history, "
            "symptoms, and prior trends. Please discuss these findings with your healthcare provider."
        )

        english_summary = "\n".join(eng_parts)

        # Build Telugu summary
        telugu_summary = TeluguHealthTranslator.generate_telugu_summary(
            patient_name=patient_name,
            observations=observations,
            medications=medications,
            english_summary=english_summary
        )

        # Default questions if none generated
        if not questions_for_doctor:
            questions_for_doctor.append("Are all of my test results within the target goals for my age and health profile?")
            questions_for_doctor.append("When do you recommend repeating these tests to monitor trends?")

        return {
            "english_summary": english_summary,
            "telugu_summary": telugu_summary,
            "key_findings": key_findings,
            "questions_for_doctor": questions_for_doctor,
            "uncertainty_notes": (
                "Reference ranges vary across laboratories and diagnostic methods. "
                "This summary is for informational guidance only and does not represent an independent clinical diagnosis."
            ),
            "is_demo_generated": True
        }
