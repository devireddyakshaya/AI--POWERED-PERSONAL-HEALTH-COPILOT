"""
Doctor Visit Prep Assistant service for MediMitra AI.
Generates relevant, patient-empowering questions to ask healthcare providers
based on abnormal test values, medication ambiguities, and trend shifts.
"""
from typing import List, Dict, Any

class DoctorPrepService:
    @staticmethod
    def generate_questions_for_document(
        observations: List[Dict[str, Any]],
        medications: List[Dict[str, Any]],
        doc_date: str = ""
    ) -> List[Dict[str, str]]:
        """
        Generates targeted doctor discussion questions from document facts.
        """
        questions = []

        # Abnormal observations
        abnormal_obs = [o for o in observations if o.get("interpretation") in ("HIGH", "LOW")]
        for obs in abnormal_obs:
            t_name = obs.get("test_name")
            val = obs.get("original_value")
            unit = obs.get("unit", "")
            ref = obs.get("reference_range_text", "")
            interp = obs.get("interpretation")

            direction = "elevated" if interp == "HIGH" else "below normal"
            questions.append({
                "question_text": f"My {t_name} was {direction} at {val} {unit} (reference: {ref}). What does this mean for my current treatment plan?",
                "context_note": f"Recorded on {doc_date or 'recent report'}",
                "category": "Abnormal Lab Follow-up"
            })

        # Incomplete medications
        for med in medications:
            m_name = med.get("medicine_name")
            if med.get("is_incomplete"):
                questions.append({
                    "question_text": f"Regarding {m_name}: Could you please confirm the exact dosage strength, daily timing, and how many weeks I should continue it?",
                    "context_note": f"Prescription instruction was flagged as incomplete ({med.get('trust_warning')})",
                    "category": "Medication Clarification"
                })
            else:
                questions.append({
                    "question_text": f"Are there any specific foods or drug interactions I should avoid while taking {m_name} ({med.get('dosage')})?",
                    "context_note": f"Daily schedule: {med.get('frequency')} - {med.get('timing_instructions')}",
                    "category": "Medication Clarification"
                })

        # General follow-up questions
        questions.append({
            "question_text": "Do you recommend repeating any of these tests in 3 to 6 months to monitor my progress?",
            "context_note": "Long-term monitoring strategy",
            "category": "Preventive Care"
        })
        questions.append({
            "question_text": "Are there any targeted lifestyle or dietary adjustments that would best support these results?",
            "context_note": "Lifestyle and nutrition guidance",
            "category": "Preventive Care"
        })

        return questions
