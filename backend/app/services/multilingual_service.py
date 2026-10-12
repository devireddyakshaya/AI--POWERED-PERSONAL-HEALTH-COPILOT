"""
Multilingual Health Explainer for MediMitra AI.
Generates short, plain-language, evidence-based explanations of a report in
English, Telugu, Hindi, Tamil, Kannada, and Malayalam.

SAFETY PRINCIPLES:
- Only values, units, test names and reference ranges actually present in the
  extracted report are used. Nothing is invented.
- No diagnosis, no dosage advice. Purely informational with a clinician referral.
- Medical test names, numbers, and units are kept in their original form so the
  meaning is never distorted across languages.
"""
from typing import Dict, Any, List

SUPPORTED_LANGUAGES = ["en", "te", "hi", "ta", "kn", "ml"]

PHRASES: Dict[str, Dict[str, str]] = {
    "en": {
        "greeting": "Hello {name}, here is a simple explanation of your {doc_type} dated {date}.",
        "intro": "This report contains {count} test result(s).",
        "high_header": "Values higher than the report's reference range:",
        "low_header": "Values lower than the report's reference range:",
        "normal_header": "Values within the reference range:",
        "med_header": "Medicines recorded:",
        "high_line": "{test} is {value} {unit}, which is above the report reference range ({ref}). Please discuss this with your doctor.",
        "low_line": "{test} is {value} {unit}, which is below the report reference range ({ref}). Please discuss this with your doctor.",
        "normal_line": "{test} is {value} {unit}, which is within the reference range ({ref}).",
        "med_line": "{name} {dose} - {freq}, {timing}.",
        "disclaimer": "This is for information only and is not a diagnosis. Always follow your doctor's advice.",
        "question_high": "My {test} is {value} {unit} (reference {ref}). What should I do next?",
        "question_low": "My {test} is {value} {unit} (reference {ref}). Should we check the cause?",
        "default_q1": "Are all my results within the goal for my age and health?",
        "default_q2": "When should I repeat these tests to track the trend?",
    },
    "te": {
        "greeting": "నమస్కారం {name} గారూ, {date} నాటి మీ {doc_type} కి సరళమైన వివరణ ఇది.",
        "intro": "ఈ నివేదికలో {count} పరీక్షల ఫలితాలు ఉన్నాయి.",
        "high_header": "నివేదిక సాధారణ పరిధి కంటే ఎక్కువ ఉన్నవి:",
        "low_header": "నివేదిక సాధారణ పరిధి కంటే తక్కువ ఉన్నవి:",
        "normal_header": "సాధారణ పరిధిలో ఉన్నవి:",
        "med_header": "నమోదైన మందులు:",
        "high_line": "{test} {value} {unit} గా ఉంది, ఇది నివేదిక సాధారణ పరిధి ({ref}) కంటే ఎక్కువ. దీనిపై మీ డాక్టర్‌ను సంప్రదించండి.",
        "low_line": "{test} {value} {unit} గా ఉంది, ఇది నివేదిక సాధారణ పరిధి ({ref}) కంటే తక్కువ. దీనిపై మీ డాక్టర్‌ను సంప్రదించండి.",
        "normal_line": "{test} {value} {unit} గా ఉంది, ఇది సాధారణ పరిధిలో ({ref}) ఉంది.",
        "med_line": "{name} {dose} - {freq}, {timing}.",
        "disclaimer": "ఇది కేవలం సమాచారం కొరకు మాత్రమే, వైద్య నిర్ధారణ కాదు. ఎప్పుడూ మీ డాక్టర్ సలహాను పాటించండి.",
        "question_high": "నా {test} {value} {unit} (సాధారణ పరిధి {ref}). ఇప్పుడు నేను ఏమి చేయాలి?",
        "question_low": "నా {test} {value} {unit} (సాధారణ పరిధి {ref}). కారణం పరిశీలించాలా?",
        "default_q1": "నా వయస్సు, ఆరోగ్యానికి నా ఫలితాలు లక్ష్యంలో ఉన్నాయా?",
        "default_q2": "ఈ పరీక్షలను మళ్లీ ఎప్పుడు చేయించుకోవాలి?",
    },
    "hi": {
        "greeting": "नमस्ते {name}, {date} की आपकी {doc_type} की सरल व्याख्या यह है।",
        "intro": "इस रिपोर्ट में {count} जाँच परिणाम हैं।",
        "high_header": "रिपोर्ट की संदर्भ सीमा से अधिक मान:",
        "low_header": "रिपोर्ट की संदर्भ सीमा से कम मान:",
        "normal_header": "संदर्भ सीमा के भीतर मान:",
        "med_header": "दर्ज दवाइयाँ:",
        "high_line": "{test} {value} {unit} है, जो रिपोर्ट की संदर्भ सीमा ({ref}) से अधिक है। कृपया अपने डॉक्टर से चर्चा करें।",
        "low_line": "{test} {value} {unit} है, जो रिपोर्ट की संदर्भ सीमा ({ref}) से कम है। कृपया अपने डॉक्टर से चर्चा करें।",
        "normal_line": "{test} {value} {unit} है, जो संदर्भ सीमा ({ref}) के भीतर है।",
        "med_line": "{name} {dose} - {freq}, {timing}.",
        "disclaimer": "यह केवल जानकारी के लिए है, निदान नहीं। हमेशा अपने डॉक्टर की सलाह लें।",
        "question_high": "मेरा {test} {value} {unit} है (संदर्भ {ref})। अब मुझे क्या करना चाहिए?",
        "question_low": "मेरा {test} {value} {unit} है (संदर्भ {ref})। कारण जाँचना चाहिए?",
        "default_q1": "क्या मेरी सभी जाँचें मेरी उम्र और स्वास्थ्य के लक्ष्य में हैं?",
        "default_q2": "ट्रेंड देखने के लिए ये जाँचें कब दोबारा करानी चाहिए?",
    },
    "ta": {
        "greeting": "வணக்கம் {name}, {date} தேதியிட்ட உங்கள் {doc_type} க்கான எளிய விளக்கம் இதுவாகும்.",
        "intro": "இந்த அறிக்கையில் {count} பரிசோதனை முடிவுகள் உள்ளன.",
        "high_header": "அறிக்கையின் குறிப்பு வரம்பை விட அதிகமான மதிப்புகள்:",
        "low_header": "அறிக்கையின் குறிப்பு வரம்பை விட குறைவான மதிப்புகள்:",
        "normal_header": "குறிப்பு வரம்பிற்குள் உள்ள மதிப்புகள்:",
        "med_header": "பதிவு செய்யப்பட்ட மருந்துகள்:",
        "high_line": "{test} {value} {unit} ஆக உள்ளது, இது அறிக்கையின் குறிப்பு வரம்பை ({ref}) விட அதிகம். உங்கள் மருத்துவரிடம் கலந்தாலோசிக்கவும்.",
        "low_line": "{test} {value} {unit} ஆக உள்ளது, இது குறிப்பு வரம்பை ({ref}) விட குறைவு. உங்கள் மருத்துவரிடம் கலந்தாலோசிக்கவும்.",
        "normal_line": "{test} {value} {unit} ஆக உள்ளது, இது குறிப்பு வரம்பிற்குள் ({ref}) உள்ளது.",
        "med_line": "{name} {dose} - {freq}, {timing}.",
        "disclaimer": "இது தகவலுக்காக மட்டுமே, நோய் கண்டறிதல் அல்ல. எப்போதும் உங்கள் மருத்துவரின் ஆலோசனையைப் பின்பற்றவும்.",
        "question_high": "எனது {test} {value} {unit} (குறிப்பு {ref}). அடுத்து நான் என்ன செய்ய வேண்டும்?",
        "question_low": "எனது {test} {value} {unit} (குறிப்பு {ref}). காரணத்தை ஆராய வேண்டுமா?",
        "default_q1": "எனது வயது மற்றும் உடல்நிலைக்கு எல்லா முடிவுகளும் இலக்கிற்குள் உள்ளதா?",
        "default_q2": "இந்த பரிசோதனைகளை மீண்டும் எப்போது செய்ய வேண்டும்?",
    },
    "kn": {
        "greeting": "ನಮಸ್ಕಾರ {name}, {date} ರಂದಿನ ನಿಮ್ಮ {doc_type} ನ ಸರಳ ವಿವರಣೆ ಇಲ್ಲಿದೆ.",
        "intro": "ಈ ವರದಿಯಲ್ಲಿ {count} ಪರೀಕ್ಷಾ ಫಲಿತಾಂಶಗಳಿವೆ.",
        "high_header": "ವರದಿಯ ಸಾಮಾನ್ಯ ವ್ಯಾಪ್ತಿಗಿಂತ ಹೆಚ್ಚಿರುವ ಮೌಲ್ಯಗಳು:",
        "low_header": "ಸಾಮಾನ್ಯ ವ್ಯಾಪ್ತಿಗಿಂತ ಕಡಿಮೆಯಿರುವ ಮೌಲ್ಯಗಳು:",
        "normal_header": "ಸಾಮಾನ್ಯ ವ್ಯಾಪ್ತಿಯಲ್ಲಿರುವ ಮೌಲ್ಯಗಳು:",
        "med_header": "ದಾಖಲಾದ ಔಷಧಿಗಳು:",
        "high_line": "{test} {value} {unit} ಇದೆ, ಇದು ವರದಿಯ ಸಾಮಾನ್ಯ ವ್ಯಾಪ್ತಿಗಿಂತ ({ref}) ಹೆಚ್ಚು. ದಯವಿಟ್ಟು ನಿಮ್ಮ ವೈದ್ಯರನ್ನು ಸಂಪರ್ಕಿಸಿ.",
        "low_line": "{test} {value} {unit} ಇದೆ, ಇದು ಸಾಮಾನ್ಯ ವ್ಯಾಪ್ತಿಗಿಂತ ({ref}) ಕಡಿಮೆ. ದಯವಿಟ್ಟು ನಿಮ್ಮ ವೈದ್ಯರನ್ನು ಸಂಪರ್ಕಿಸಿ.",
        "normal_line": "{test} {value} {unit} ಇದೆ, ಇದು ಸಾಮಾನ್ಯ ವ್ಯಾಪ್ತಿಯಲ್ಲಿದೆ ({ref}).",
        "med_line": "{name} {dose} - {freq}, {timing}.",
        "disclaimer": "ಇದು ಕೇವಲ ಮಾಹಿತಿಗಾಗಿ, ರೋಗನಿರ್ಣಯ ಅಲ್ಲ. ಯಾವಾಗಲೂ ನಿಮ್ಮ ವೈದ್ಯರ ಸಲಹೆ ಪಾಲಿಸಿ.",
        "question_high": "ನನ್ನ {test} {value} {unit} (ಸಾಮಾನ್ಯ ವ್ಯಾಪ್ತಿ {ref}). ಮುಂದೆ ನಾನು ಏನು ಮಾಡಬೇಕು?",
        "question_low": "ನನ್ನ {test} {value} {unit} (ಸಾಮಾನ್ಯ ವ್ಯಾಪ್ತಿ {ref}). ಕಾರಣ ಪರಿಶೀಲಿಸಬೇಕೇ?",
        "default_q1": "ನನ್ನ ವಯಸ್ಸು ಮತ್ತು ಆರೋಗ್ಯಕ್ಕೆ ಎಲ್ಲಾ ಫಲಿತಾಂಶಗಳು ಗುರಿಯಲ್ಲಿವೆಯೇ?",
        "default_q2": "ಈ ಪರೀಕ್ಷೆಗಳನ್ನು ಮತ್ತೆ ಯಾವಾಗ ಮಾಡಿಸಬೇಕು?",
    },
    "ml": {
        "greeting": "നമസ്കാരം {name}, {date} തീയതിയിലെ നിങ്ങളുടെ {doc_type} ന്റെ ലളിതമായ വിശദീകരണം ഇതാണ്.",
        "intro": "ഈ റിപ്പോർട്ടിൽ {count} പരിശോധനാ ഫലങ്ങളുണ്ട്.",
        "high_header": "റിപ്പോർട്ടിലെ സാധാരണ പരിധിയേക്കാൾ ഉയർന്ന മൂല്യങ്ങൾ:",
        "low_header": "സാധാരണ പരിധിയേക്കാൾ കുറഞ്ഞ മൂല്യങ്ങൾ:",
        "normal_header": "സാധാരണ പരിധിയിലുള്ള മൂല്യങ്ങൾ:",
        "med_header": "രേഖപ്പെടുത്തിയ മരുന്നുകൾ:",
        "high_line": "{test} {value} {unit} ആണ്, ഇത് റിപ്പോർട്ടിലെ സാധാരണ പരിധിയേക്കാൾ ({ref}) കൂടുതലാണ്. ദയവായി ഡോക്ടറെ കാണുക.",
        "low_line": "{test} {value} {unit} ആണ്, ഇത് സാധാരണ പരിധിയേക്കാൾ ({ref}) കുറവാണ്. ദയവായി ഡോക്ടറെ കാണുക.",
        "normal_line": "{test} {value} {unit} ആണ്, ഇത് സാധാരണ പരിധിയിലാണ് ({ref}).",
        "med_line": "{name} {dose} - {freq}, {timing}.",
        "disclaimer": "ഇത് വിവരത്തിന് മാത്രമുള്ളതാണ്, രോഗനിർണയമല്ല. എപ്പോഴും ഡോക്ടറുടെ ഉപദേശം പാലിക്കുക.",
        "question_high": "എന്റെ {test} {value} {unit} (പരിധി {ref}). ഇനി ഞാൻ എന്ത് ചെയ്യണം?",
        "question_low": "എന്റെ {test} {value} {unit} (പരിധി {ref}). കാരണം പരിശോധിക്കണോ?",
        "default_q1": "എന്റെ പ്രായത്തിനും ആരോഗ്യത്തിനും എല്ലാ ഫലങ്ങളും ലക്ഷ്യത്തിലാണോ?",
        "default_q2": "ഈ പരിശോധനകൾ വീണ്ടും എപ്പോൾ ചെയ്യണം?",
    },
}


class MultilingualHealthExplainer:
    @staticmethod
    def supported_languages() -> List[str]:
        return list(SUPPORTED_LANGUAGES)

    @staticmethod
    def build(
        language: str,
        patient_name: str,
        document_type: str,
        document_date: str,
        observations: List[Dict[str, Any]],
        medications: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Builds a concise, localized explanation strictly from the extracted data.
        """
        lang = language if language in PHRASES else "en"
        p = PHRASES[lang]

        abnormal_high = [o for o in observations if o.get("interpretation") == "HIGH"]
        abnormal_low = [o for o in observations if o.get("interpretation") == "LOW"]
        normal_obs = [o for o in observations if o.get("interpretation") == "NORMAL"]

        parts: List[str] = []
        parts.append(p["greeting"].format(
            name=patient_name,
            doc_type=document_type,
            date=document_date or ""
        ))
        parts.append(p["intro"].format(count=len(observations)))

        def fmt_line(obs: Dict[str, Any], key: str) -> str:
            return p[key].format(
                test=obs.get("test_name", ""),
                value=obs.get("original_value", ""),
                unit=obs.get("unit") or "",
                ref=obs.get("reference_range_text") or "N/A"
            )

        if abnormal_high:
            parts.append("\n" + p["high_header"])
            for o in abnormal_high:
                parts.append("• " + fmt_line(o, "high_line"))
        if abnormal_low:
            parts.append("\n" + p["low_header"])
            for o in abnormal_low:
                parts.append("• " + fmt_line(o, "low_line"))
        if normal_obs:
            parts.append("\n" + p["normal_header"])
            for o in normal_obs:
                parts.append("• " + fmt_line(o, "normal_line"))

        if medications:
            parts.append("\n" + p["med_header"])
            for m in medications:
                parts.append("• " + p["med_line"].format(
                    name=m.get("medicine_name", ""),
                    dose=m.get("dosage") or "",
                    freq=m.get("frequency") or "",
                    timing=m.get("timing_instructions") or ""
                ))

        parts.append("\n" + p["disclaimer"])
        summary = "\n".join(parts)

        # Structured findings (kept short, no long paragraphs)
        key_findings = []
        for o in observations:
            interp = o.get("interpretation", "UNCERTAIN")
            if interp == "HIGH":
                finding = fmt_line(o, "high_line")
                f_interp = "ABNORMAL_HIGH"
            elif interp == "LOW":
                finding = fmt_line(o, "low_line")
                f_interp = "ABNORMAL_LOW"
            else:
                finding = fmt_line(o, "normal_line")
                f_interp = "NORMAL"
            key_findings.append({
                "title": o.get("test_name", ""),
                "finding": finding,
                "interpretation": f_interp,
                "evidence_excerpt": o.get("evidence_excerpt", ""),
                "reference_range": o.get("reference_range_text"),
                "needs_verification": float(o.get("confidence_score", 1.0) or 1.0) < 0.85
            })

        questions: List[str] = []
        for o in abnormal_high:
            questions.append(p["question_high"].format(
                test=o.get("test_name", ""),
                value=o.get("original_value", ""),
                unit=o.get("unit") or "",
                ref=o.get("reference_range_text") or "N/A"
            ))
        for o in abnormal_low:
            questions.append(p["question_low"].format(
                test=o.get("test_name", ""),
                value=o.get("original_value", ""),
                unit=o.get("unit") or "",
                ref=o.get("reference_range_text") or "N/A"
            ))
        if not questions:
            questions = [p["default_q1"], p["default_q2"]]

        return {
            "language": lang,
            "summary": summary,
            "key_findings": key_findings,
            "questions_for_doctor": questions,
            "uncertainty_notes": p["disclaimer"]
        }
