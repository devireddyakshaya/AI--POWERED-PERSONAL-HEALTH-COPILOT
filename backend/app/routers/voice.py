"""
Voice Assistant intelligence route for MediMitra AI.
Answers free-text questions (spoken or typed) using the patient's extracted
reports. Uses Gemini when configured, with a deterministic, medically-safe
Demo Mode fallback so the assistant always replies.
"""
import logging
import re
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models import HealthDocument
from backend.app.services.ai_service import GEMINI_CLIENT, is_demo_mode
from backend.app.services.multilingual_service import MultilingualHealthExplainer, PHRASES

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/voice", tags=["Voice Assistant"])

# Reuse the multilingual template strings for localized fallback answers.
PHRASE_TEMPLATES = PHRASES
HELPER_PHRASES: Dict[str, Dict[str, str]] = {
    "en": {
        "no_report": "Please upload a report first, then ask me your question again.",
        "no_match": "I could not find that information in your report. You can ask me about any test value, or say read my report for a full summary.",
        "questions": "You can say: read my report, show my medications, show my timeline, or ask about any test in your report.",
    },
    "te": {
        "no_report": "ముందుగా ఒక నివేదికను అప్లోడ్ చేయండి, తర్వాత మీ ప్రశ్నను మళ్ళీ అడగండి.",
        "no_match": "మీ నివేదికలో ఆ సమాచారం కనుగొనలేకపోయాను. ఏదైనా పరీక్ష విలువ గురించి అడగవచ్చు, లేదా పూర్తి సారాంశం కోసం నా నివేదిక చదువు అని చెప్పండి.",
        "questions": "మీరు ఇలా అడగవచ్చు: నా నివేదిక చదువు, నా మందులు చూపించు, టైమ్ లైన్ చూపించు, లేదా నివేదికలోని ఏదైనా పరీక్ష గురించి అడగండి.",
    },
    "hi": {
        "no_report": "कृपया पहले एक रिपोर्ट अपलोड करें, फिर दोबारा अपना प्रश्न पूछें।",
        "no_match": "मुझे आपकी रिपोर्ट में वह जानकारी नहीं मिली। आप किसी भी जाँच के बारे में पूछ सकते हैं, या संपूर्ण सारांश के लिए मेरी रिपोर्ट पढ़ो कहें।",
        "questions": "आप कह सकते हैं: मेरी रिपोर्ट पढ़ो, मेरी दवाइयाँ दिखाओ, मेरी टाइमलाइन दिखाओ, या रिपोर्ट की किसी भी जाँच के बारे में पूछें।",
    },
    "ta": {
        "no_report": "முதலில் ஒரு அறிக்கையை பதிவேற்றவும், பிறகு உங்கள் கேள்வியை மீண்டும் கேளுங்கள்.",
        "no_match": "உங்கள் அறிக்கையில் அந்த தகவலை என்னால் கண்டுபிடிக்க முடியவில்லை. எந்த பரிசோதனை மதிப்பு குறித்தும் கேட்கலாம், அல்லது முழு சுருக்கத்திற்கு என் அறிக்கையை வாசி என்று சொல்லுங்கள்.",
        "questions": "நீங்கள் கேட்கலாம்: என் அறிக்கையை வாசி, என் மருந்துகளைக் காட்டு, என் டைம்லைனைக் காட்டு, அல்லது அறிக்கையில் உள்ள எந்த பரிசோதனை பற்றியும் கேளுங்கள்.",
    },
    "kn": {
        "no_report": "ಮೊದಲು ಒಂದು ವರದಿಯನ್ನು ಅಪ್‌ಲೋಡ್ ಮಾಡಿ, ನಂತರ ನಿಮ್ಮ ಪ್ರಶ್ನೆಯನ್ನು ಮತ್ತೆ ಕೇಳಿ.",
        "no_match": "ನಿಮ್ಮ ವರದಿಯಲ್ಲಿ ಆ ಮಾಹಿತಿ ನನಗೆ ಸಿಗಲಿಲ್ಲ. ಯಾವುದೇ ಪರೀಕ್ಷಾ ಮೌಲ್ಯದ ಬಗ್ಗೆ ಕೇಳಬಹುದು, ಅಥವಾ ಪೂರ್ಣ ಸಾರಾಂಶಕ್ಕಾಗಿ ನನ್ನ ವರದಿಯನ್ನು ಓದು ಎಂದು ಹೇಳಿ.",
        "questions": "ನೀವು ಹೇಗೆ ಕೇಳಬಹುದು: ನನ್ನ ವರದಿಯನ್ನು ಓದು, ನನ್ನ ಔಷಧಿಗಳನ್ನು ತೋರಿಸು, ನನ್ನ ಟೈಮ್‌ಲೈನ್ ತೋರಿಸು, ಅಥವಾ ವರದಿಯ ಯಾವುದೇ ಪರೀಕ್ಷೆಯ ಬಗ್ಗೆ ಕೇಳಿ.",
    },
    "ml": {
        "no_report": "ആദ്യം ഒരു റിപ്പോർട്ട് അപ്‌ലോഡ് ചെയ്യുക, എന്നിട്ട് നിങ്ങളുടെ ചോദ്യം വീണ്ടും ചോദിക്കുക.",
        "no_match": "നിങ്ങളുടെ റിപ്പോർട്ടിൽ ആ വിവരം എനിക്ക് കണ്ടെത്താനായില്ല. ഏത് പരിശോധനാ മൂല്യത്തെക്കുറിച്ചും ചോദിക്കാം, അല്ലെങ്കിൽ പൂർണ്ണ സംഗ്രഹത്തിനായി എന്റെ റിപ്പോർട്ട് വായിക്കൂ എന്ന് പറയുക.",
        "questions": "നിങ്ങൾക്ക് ചോദിക്കാം: എന്റെ റിപ്പോർട്ട് വായിക്കൂ, എന്റെ മരുന്നുകൾ കാണിക്കൂ, എന്റെ ടൈംലൈൻ കാണിക്കൂ, അല്ലെങ്കിൽ റിപ്പോർട്ടിലെ ഏത് പരിശോധനയെക്കുറിച്ചും ചോദിക്കാം.",
    },
}

SAFE_ANSWER_PROMPT = """You are MediMitra AI, an empathetic and medically safe health assistant.
Answer the patient's question in {language} based ONLY on the report data provided below.
Rules:
1. INFORMATIONAL ONLY — never diagnose. Say 'outside the reference range and needs clinical correlation by your doctor' instead of diagnosing.
2. Never prescribe, change, or suggest dosages.
3. Keep test names, numbers and units exactly as in the report.
4. Reply in at most 4 short, spoken sentences in the requested language.
5. End with: consult your doctor for an accurate interpretation.

REPORT DATA:
{context}

PATIENT QUESTION: {query}
"""

MEDICAL_KEYWORDS_EN = ["medicine", "medication", "meds", "drug", "tablet", "pills", "prescription"]
MEDICAL_KEYWORDS = {
    "te": ["మందు", "మందులు"],
    "hi": ["दवा", "दवाइयाँ", "दवाई"],
    "ta": ["மருந்து"],
    "kn": ["ಔಷಧ", "ಮಾತ್ರೆ"],
    "ml": ["മരുന്ന"],
}

# Synonyms mapping a spoken/keyboard term to a fragment of the canonical test name.
# This lets questions like "what is my sugar?" match "Fasting Blood Glucose".
TEST_SYNONYMS: Dict[str, List[str]] = {
    "glucose": ["sugar", "glucose", "fbs", "blood sugar", "fasting sugar", "diabetes"],
    "hba1c": ["hba1c", "a1c", "glycated", "glycosylated", "average sugar"],
    "cholesterol": ["cholesterol", "total cholesterol"],
    "ldl": ["ldl", "bad cholesterol"],
    "hdl": ["hdl", "good cholesterol"],
    "triglyceride": ["triglyceride", "triglycerides", "tg"],
    "creatinine": ["creatinine", "kidney"],
    "urea": ["urea", "bun"],
    "hemoglobin": ["hemoglobin", "haemoglobin", "hb"],
    "leukocyte": ["wbc", "leukocyte", "white blood", "tlc"],
    "platelet": ["platelet", "platelets"],
    "tsh": ["tsh", "thyroid"],
    "bilirubin": ["bilirubin"],
    "sgpt": ["sgpt", "alt", "liver"],
    "sgpt / alt": ["sgpt", "alt"],
    "uric": ["uric", "gout"],
    "troponin": ["troponin"],
    "ck-mb": ["ck-mb", "ckmb", "cpk"],
    "bnp": ["bnp", "probnp", "nt-probnp"],
    "homocysteine": ["homocysteine"],
    "vitamin b12": ["b12", "cobalamin", "vitamin b12"],
    "folate": ["folate", "folic"],
    "fsh": ["fsh", "follicle"],
    "luteinizing": ["lh", "luteinizing"],
    "estradiol": ["estradiol", "e2", "estrogen"],
    "prolactin": ["prolactin"],
    "hcg": ["hcg", "pregnancy", "beta hcg"],
}

SPECIALTY_PHRASE: Dict[str, str] = {
    "en": "This appears to be a {specialty} report.",
    "te": "ఇది {specialty} నివేదికలా కనిపిస్తోంది.",
    "hi": "यह एक {specialty} रिपोर्ट प्रतीत होती है।",
    "ta": "இது ஒரு {specialty} அறிக்கையாகத் தெரிகிறது.",
    "kn": "ಇದು {specialty} ವರದಿ ಎಂದು ತೋರುತ್ತದೆ.",
    "ml": "ഇത് ഒരു {specialty} റിപ്പോർട്ടായി തോന്നുന്നു.",
}


class AskRequest(BaseModel):
    query: str
    language: str = "en"
    document_id: Optional[int] = None


class AskResponse(BaseModel):
    answer: str
    query: str
    language: str
    document_id: Optional[int] = None
    source: str = "demo"


def _pick_lang(language: str) -> str:
    return language if language in MultilingualHealthExplainer.supported_languages() else "en"


def _doc_context(doc: HealthDocument) -> str:
    """Serializes the extracted observations and medications of a document."""
    lines: List[str] = []
    for o in doc.observations:
        lines.append(
            f"- {o.test_name}: {o.user_corrected_value or o.original_value} {o.unit or ''} "
            f"(reference {o.reference_range_text or 'N/A'}) - {o.interpretation}"
        )
    for m in doc.medications:
        lines.append(
            f"- Rx {m.medicine_name} {m.dosage or ''} {m.frequency or ''} "
            f"{m.timing_instructions or ''}".strip()
        )
    return "\n".join(lines) or "No data available."


@router.post("/ask", response_model=AskResponse)
def voice_ask(payload: AskRequest, db: Session = Depends(get_db)):
    """Returns a spoken-ready answer for a free-text health question."""
    query = (payload.query or "").strip()
    lang = _pick_lang(payload.language)

    if not query:
        return AskResponse(answer=HELPER_PHRASES[lang]["questions"], query=query, language=lang)

    doc = None
    if payload.document_id:
        doc = db.query(HealthDocument).filter(HealthDocument.id == payload.document_id).first()

    if doc is None:
        # Fall back to the most recently uploaded document so the assistant can
        # still answer when no specific report is selected.
        doc = db.query(HealthDocument).order_by(HealthDocument.id.desc()).first()

    if doc is None:
        return AskResponse(answer=HELPER_PHRASES[lang]["no_report"], query=query, language=lang)

    if not is_demo_mode() and GEMINI_CLIENT is not None:
        try:
            return _ask_gemini(payload, query, lang, doc)
        except Exception as exc:  # pragma: no cover - depends on external API
            logger.warning(f"Gemini voice answer failed, using fallback: {exc}")

    return AskResponse(
        answer=_deterministic_answer(query, lang, doc),
        query=query,
        language=lang,
        document_id=doc.id,
        source="demo"
    )


def _ask_gemini(payload: AskRequest, query: str, lang: str, doc: HealthDocument):
    """Invokes Gemini for a concise spoken answer in the requested language."""
    model = GEMINI_CLIENT.GenerativeModel(model_name="gemini-1.5-flash")
    prompt = SAFE_ANSWER_PROMPT.format(
        language=lang,
        context=_doc_context(doc),
        query=query
    )
    response = model.generate_content(prompt)
    return AskResponse(
        answer=response.text.strip() or HELPER_PHRASES[lang]["no_match"],
        query=query,
        language=lang,
        document_id=doc.id,
        source="gemini"
    )


def _match_observation(q: str, obs_list: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """
    Finds the observation a question is about, using the canonical test name
    first and a synonym map second (so 'sugar' can match 'Fasting Blood Glucose').
    """
    q_lower = q.lower()
    for o in obs_list:
        name = (o.get("test_name") or "").lower()
        if name and name in q_lower:
            return o

    for canonical_fragment, synonyms in TEST_SYNONYMS.items():
        matching_obs = next(
            (o for o in obs_list if canonical_fragment in (o.get("test_name") or "").lower()),
            None
        )
        if not matching_obs:
            continue
        for syn in synonyms:
            if re.search(rf"\b{re.escape(syn)}\b", q_lower):
                return matching_obs
    return None


def _deterministic_answer(query: str, lang: str, doc: HealthDocument) -> str:
    """Builds a safe, report-grounded, spoken-friendly answer without any external API."""
    q = query.lower()
    p = PHRASE_TEMPLATES.get(lang, PHRASE_TEMPLATES["en"])
    disclaimer = p["disclaimer"]

    obs_list = [
        {
            "test_name": o.test_name,
            "original_value": o.user_corrected_value or o.original_value,
            "unit": o.unit or "",
            "reference_range_text": o.reference_range_text or "N/A",
            "interpretation": o.interpretation,
            "confidence_score": o.confidence_score,
        }
        for o in doc.observations
    ]
    med_list = list(doc.medications)

    # 1) Question about a specific test -> answer only that test.
    matched = _match_observation(query, obs_list)
    if matched:
        return _test_answer(p, matched, disclaimer)

    # 2) Question about medicines -> list recorded medicines.
    med_hits = MEDICAL_KEYWORDS_EN + MEDICAL_KEYWORDS.get(lang, [])
    if med_list and any(kw in q for kw in med_hits):
        lines = [p["med_header"]]
        for m in med_list:
            lines.append("• " + p["med_line"].format(
                name=m.medicine_name,
                dose=m.dosage or "",
                freq=m.frequency or "",
                timing=m.timing_instructions or ""
            ))
        lines.append(p["disclaimer"])
        return "\n".join(lines)

    # 3) General question -> short, grounded, spoken summary.
    return _spoken_summary(lang, p, doc, obs_list, med_list, disclaimer)


def _spoken_summary(
    lang: str,
    p: Dict[str, str],
    doc: HealthDocument,
    obs_list: List[Dict[str, Any]],
    med_list: List[Any],
    disclaimer: str
) -> str:
    """A concise spoken summary: specialty, key abnormal values, and medicines."""
    lines: List[str] = []
    specialty = getattr(doc, "specialty", None)

    if specialty and specialty != "General Medicine":
        phrase = SPECIALTY_PHRASE.get(lang, SPECIALTY_PHRASE["en"])
        lines.append(phrase.format(specialty=specialty))

    abnormal = [o for o in obs_list if o.get("interpretation") in ("HIGH", "LOW")]
    if abnormal:
        for o in abnormal[:3]:
            lines.append(_test_answer(p, o, "").strip())
    elif obs_list:
        lines.append(_test_answer(p, obs_list[0], "").strip())
    else:
        return HELPER_PHRASES[lang]["no_match"]

    if med_list:
        names = ", ".join(m.medicine_name for m in med_list[:4])
        lines.append(f"{p['med_header']} {names}.")

    lines.append(disclaimer)
    return " ".join(lines)


def _test_answer(p: Dict[str, str], obs: Dict[str, Any], disclaimer: str) -> str:
    interp = obs.get("interpretation", "UNCERTAIN")
    if interp == "HIGH":
        line = p["high_line"]
    elif interp == "LOW":
        line = p["low_line"]
    else:
        line = p["normal_line"]
    sentence = line.format(
        test=obs["test_name"],
        value=obs["original_value"],
        unit=obs["unit"],
        ref=obs["reference_range_text"],
    )
    return f"{sentence} {disclaimer}"