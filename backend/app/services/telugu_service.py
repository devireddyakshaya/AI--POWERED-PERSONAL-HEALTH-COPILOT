"""
Telugu Health Translator service for MediMitra AI.
Generates natural, respectful Telugu (తెలుగు) medical explanations.
Strictly preserves medicine names, numerical values, units, and dates unchanged.
Does not alter clinical meaning.
"""
from typing import Dict, Any, List

# Standard medical term explanations in Telugu
TELUGU_MEDICAL_GLOSSARY = {
    "Fasting Blood Glucose": "ఉపవాస రక్త చక్కెర (Fasting Blood Glucose)",
    "HbA1c (Glycated Hemoglobin)": "గత 3 నెలల సగటు చక్కెర స్థాయి (HbA1c)",
    "Total Cholesterol": "రక్తంలోని మొత్తం కొలెస్ట్రాల్ (Total Cholesterol)",
    "Triglycerides": "రక్తంలో కొవ్వు కణాలు (Triglycerides)",
    "HDL Cholesterol": "మంచి కొలెస్ట్రాల్ (HDL Cholesterol)",
    "LDL Cholesterol": "చెడు కొలెస్ట్రాల్ (LDL Cholesterol)",
    "Serum Creatinine": "కిడ్నీ పనితీరును సూచించే క్రియాటినిన్ (Serum Creatinine)",
    "Hemoglobin (Hb)": "రక్తంలోని హిమోగ్లోబిన్ / రక్త పరిమాణం (Hemoglobin)",
    "Thyroid Stimulating Hormone (TSH)": "థైరాయిడ్ హార్మోన్ స్థాయి (TSH)",
    "HIGH": "సాధారణ పరిమితి కంటే ఎక్కువ (High)",
    "LOW": "సాధారణ పరిమితి కంటే తక్కువ (Low)",
    "NORMAL": "సాధారణ పరిధిలోనే ఉంది (Normal)"
}

class TeluguHealthTranslator:
    @staticmethod
    def generate_telugu_summary(
        patient_name: str,
        observations: List[Dict[str, Any]],
        medications: List[Dict[str, Any]],
        english_summary: str
    ) -> str:
        """
        Generates patient-friendly Telugu summary.
        Keeps medicine names, numerical values, units, and dates in original form.
        """
        abnormal_obs = [obs for obs in observations if obs.get("interpretation") in ("HIGH", "LOW")]
        normal_obs = [obs for obs in observations if obs.get("interpretation") == "NORMAL"]

        parts = []
        parts.append(f"నమస్కారం {patient_name} గారూ, మీ ఆరోగ్య నివేదిక వివరాలు కింద సరళమైన తెలుగులో ఇవ్వబడ్డాయి:")

        if abnormal_obs:
            parts.append("\n📌 మీ వైద్యునితో చర్చించవలసిన ముఖ్యమైన పరీక్షలు:")
            for obs in abnormal_obs:
                t_name = obs.get("test_name", "")
                val = obs.get("original_value", "")
                unit = obs.get("unit", "")
                ref = obs.get("reference_range_text", "")
                interp = obs.get("interpretation", "")
                interp_te = "సాధారణ పరిమితి కంటే ఎక్కువ (High)" if interp == "HIGH" else "సాధారణ పరిమితి కంటే తక్కువ (Low)"

                parts.append(
                    f"• {t_name}: ప్రస్తుతం {val} {unit} గా ఉంది ({interp_te}). "
                    f"ఈ నివేదిక ప్రకారం సాధారణ పరిధి {ref}. "
                    f"ఈ ఫలితం గురించి మీ డాక్టర్‌ను సంప్రదించి సలహా తీసుకోండి."
                )

        if normal_obs:
            parts.append("\n✅ సాధారణ పరిధిలోనే ఉన్న పరీక్షలు:")
            normal_names = [f"{o['test_name']} ({o['original_value']} {o['unit']})" for o in normal_obs]
            parts.append("• " + ", ".join(normal_names) + " సాధారణ పరిధిలోనే నమోదయ్యాయి.")

        if medications:
            parts.append("\n💊 సూచించిన మందుల వివరాలు:")
            for med in medications:
                m_name = med.get("medicine_name", "")
                dose = med.get("dosage", "నిర్దేశించిన మోతాదు")
                freq = med.get("frequency", "")
                timing = med.get("timing_instructions", "")
                parts.append(f"• {m_name} ({dose}): {freq} - {timing}. డాక్టర్ చెప్పిన సమయానికి మాత్రమే వాడండి.")

        parts.append(
            "\n⚠️ గమనిక: ఇది కేవలం సమాచార ప్రయోజనాల కొరకు మాత్రమే. ఇది వైద్య నిర్ధారణ లేదా చికిత్సకు ప్రత్యామ్నాయం కాదు. "
            "ఏదైనా మార్పుల కొరకు అర్హత కలిగిన మీ వైద్యుడిని సంప్రదించండి."
        )

        return "\n".join(parts)
