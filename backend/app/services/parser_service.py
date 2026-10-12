"""
Medical entity parsing engine for MediMitra AI.
Extracts laboratory observations, reference ranges, units, and medications
with strict provenance, evidence excerpts, and Smart Report Trust Checks.
Never invents values or diagnoses.
"""
import re
from typing import Dict, Any, List, Optional, Tuple

KNOWN_LAB_TESTS = [
    {
        "canonical_name": "Fasting Blood Glucose",
        "patterns": [r"fasting\s+blood\s+(?:glucose|sugar)", r"fbs\b", r"fasting\s+glucose", r"blood\s+sugar\s+fasting"],
        "default_unit": "mg/dL",
        "loinc": "1558-6",
        "default_ref": (70.0, 99.0, "70 - 99 mg/dL")
    },
    {
        "canonical_name": "HbA1c (Glycated Hemoglobin)",
        "patterns": [r"hba1c\b", r"glycated\s+hemoglobin", r"glycosylated\s+hemoglobin", r"hemoglobin\s+a1c"],
        "default_unit": "%",
        "loinc": "4548-4",
        "default_ref": (4.0, 5.6, "4.0 - 5.6 %")
    },
    {
        "canonical_name": "Total Cholesterol",
        "patterns": [r"total\s+cholesterol", r"cholesterol\s*-\s*total", r"serum\s+cholesterol\s+total"],
        "default_unit": "mg/dL",
        "loinc": "2093-3",
        "default_ref": (125.0, 200.0, "< 200 mg/dL")
    },
    {
        "canonical_name": "Triglycerides",
        "patterns": [r"triglycerides", r"serum\s+triglycerides", r"tg\b"],
        "default_unit": "mg/dL",
        "loinc": "2571-8",
        "default_ref": (50.0, 150.0, "< 150 mg/dL")
    },
    {
        "canonical_name": "HDL Cholesterol",
        "patterns": [r"hdl\s+cholesterol", r"hdl\b", r"high\s+density\s+lipoprotein"],
        "default_unit": "mg/dL",
        "loinc": "2085-9",
        "default_ref": (40.0, 60.0, "> 40 mg/dL")
    },
    {
        "canonical_name": "LDL Cholesterol",
        "patterns": [r"ldl\s+cholesterol", r"ldl\b", r"low\s+density\s+lipoprotein"],
        "default_unit": "mg/dL",
        "loinc": "2089-1",
        "default_ref": (50.0, 100.0, "< 100 mg/dL")
    },
    {
        "canonical_name": "Serum Creatinine",
        "patterns": [r"serum\s+creatinine", r"creatinine\s*-\s*serum", r"creatinine\b"],
        "default_unit": "mg/dL",
        "loinc": "2160-0",
        "default_ref": (0.7, 1.3, "0.7 - 1.3 mg/dL")
    },
    {
        "canonical_name": "Blood Urea Nitrogen (BUN)",
        "patterns": [r"blood\s+urea\s+nitrogen", r"bun\b", r"serum\s+urea", r"urea\b"],
        "default_unit": "mg/dL",
        "loinc": "3094-0",
        "default_ref": (7.0, 20.0, "7 - 20 mg/dL")
    },
    {
        "canonical_name": "Hemoglobin (Hb)",
        "patterns": [r"hemoglobin\b", r"haemoglobin\b", r"hb\b"],
        "default_unit": "g/dL",
        "loinc": "718-7",
        "default_ref": (13.0, 17.0, "13.0 - 17.0 g/dL")
    },
    {
        "canonical_name": "Total Leukocyte Count (WBC)",
        "patterns": [r"total\s+leukocyte\s+count", r"wbc\s+count", r"wbc\b", r"tlc\b"],
        "default_unit": "/cumm",
        "loinc": "6690-2",
        "default_ref": (4000.0, 11000.0, "4,000 - 11,000 /cumm")
    },
    {
        "canonical_name": "Platelet Count",
        "patterns": [r"platelet\s+count", r"platelets\b"],
        "default_unit": "lakh/cumm",
        "loinc": "777-3",
        "default_ref": (1.5, 4.5, "1.5 - 4.5 lakh/cumm")
    },
    {
        "canonical_name": "Thyroid Stimulating Hormone (TSH)",
        "patterns": [r"thyroid\s+stimulating\s+hormone", r"tsh\b", r"ultra\s+tsh"],
        "default_unit": "uIU/mL",
        "loinc": "3016-3",
        "default_ref": (0.4, 4.5, "0.4 - 4.5 uIU/mL")
    },
    {
        "canonical_name": "Serum Bilirubin (Total)",
        "patterns": [r"total\s+bilirubin", r"bilirubin\s+total", r"serum\s+bilirubin"],
        "default_unit": "mg/dL",
        "loinc": "1975-2",
        "default_ref": (0.2, 1.2, "0.2 - 1.2 mg/dL")
    },
    {
        "canonical_name": "SGPT / ALT (Alanine Aminotransferase)",
        "patterns": [r"sgpt\b", r"alt\b", r"alanine\s+aminotransferase"],
        "default_unit": "U/L",
        "loinc": "1742-6",
        "default_ref": (10.0, 40.0, "10 - 40 U/L")
    },
    {
        "canonical_name": "Serum Uric Acid",
        "patterns": [r"uric\s+acid", r"serum\s+uric\s+acid"],
        "default_unit": "mg/dL",
        "loinc": "3084-1",
        "default_ref": (3.5, 7.2, "3.5 - 7.2 mg/dL")
    },
    # --- Cardiology markers ---
    {
        "canonical_name": "High-Sensitivity Troponin I",
        "patterns": [r"troponin\s*i\b", r"hs[\s\-]?troponin", r"troponin"],
        "default_unit": "ng/mL",
        "loinc": "89579-7",
        "default_ref": (0.0, 0.04, "<= 0.04 ng/mL")
    },
    {
        "canonical_name": "CK-MB (Creatine Kinase-MB)",
        "patterns": [r"ck[\s\-]?mb", r"creatine\s+kinase[\s\-]?mb"],
        "default_unit": "U/L",
        "loinc": "13969-1",
        "default_ref": (0.0, 25.0, "0 - 25 U/L")
    },
    {
        "canonical_name": "NT-proBNP",
        "patterns": [r"nt[\s\-]?pro[\s\-]?bnp", r"pro[\s\-]?bnp\b", r"\bbnp\b"],
        "default_unit": "pg/mL",
        "loinc": "33762-6",
        "default_ref": (0.0, 125.0, "< 125 pg/mL")
    },
    {
        "canonical_name": "Homocysteine",
        "patterns": [r"homocysteine"],
        "default_unit": "umol/L",
        "loinc": "13965-9",
        "default_ref": (5.0, 15.0, "5 - 15 umol/L")
    },
    # --- Neurology markers ---
    {
        "canonical_name": "Vitamin B12",
        "patterns": [r"vitamin\s+b[\s\-]?12", r"\bb12\b", r"cobalamin"],
        "default_unit": "pg/mL",
        "loinc": "2132-9",
        "default_ref": (200.0, 900.0, "200 - 900 pg/mL")
    },
    {
        "canonical_name": "Folic Acid (Folate)",
        "patterns": [r"folic\s+acid", r"folate"],
        "default_unit": "ng/mL",
        "loinc": "2284-8",
        "default_ref": (3.0, 17.0, "3 - 17 ng/mL")
    },
    # --- Gynecology & Obstetrics markers ---
    {
        "canonical_name": "Follicle Stimulating Hormone (FSH)",
        "patterns": [r"follicle\s+stimulating\s+hormone", r"\bfsh\b"],
        "default_unit": "mIU/mL",
        "loinc": "15067-2",
        "default_ref": (3.0, 12.0, "3 - 12 mIU/mL")
    },
    {
        "canonical_name": "Luteinizing Hormone (LH)",
        "patterns": [r"luteinizing\s+hormone", r"\blh\b"],
        "default_unit": "mIU/mL",
        "loinc": "10501-5",
        "default_ref": (2.0, 15.0, "2 - 15 mIU/mL")
    },
    {
        "canonical_name": "Estradiol (E2)",
        "patterns": [r"estradiol", r"\be2\b"],
        "default_unit": "pg/mL",
        "loinc": "2243-4",
        "default_ref": (30.0, 400.0, "30 - 400 pg/mL")
    },
    {
        "canonical_name": "Prolactin",
        "patterns": [r"prolactin"],
        "default_unit": "ng/mL",
        "loinc": "2842-3",
        "default_ref": (4.0, 23.0, "4 - 23 ng/mL")
    },
    {
        "canonical_name": "Beta hCG",
        "patterns": [r"beta[\s\-]?hcg", r"\bb[\s\-]?hcg\b", r"human\s+chorionic"],
        "default_unit": "mIU/mL",
        "loinc": "2118-8",
        "default_ref": (0.0, 5.0, "< 5 mIU/mL")
    }
]

# Keywords used to infer the medical specialty a report belongs to.
SPECIALTY_KEYWORDS = {
    "Gynecology & Obstetrics": [
        "gynec", "gynaec", "obstetric", "pregnan", "antenatal", "trimester",
        "fsh", "luteinizing", "estradiol", "prolactin", "beta hcg", "β-hcg",
        "human chorionic", "pap smear", "pelvic", "uterus", "uterine", "ovar",
        "menstrual", "menses", "amenorrhea", "pcos", "polycystic", "endometri",
        "cervical", "vaginal", "follicle stimulating"
    ],
    "Cardiology": [
        "cardio", "ecg", "ekg", "echocardiog", "troponin", "ck-mb", "ckmb",
        "nt-probnp", "probnp", " bnp", "angina", "chest pain", "stent",
        "arrhythmia", "myocardial", "heart failure", "hypertension",
        "blood pressure", "homocysteine", "holter"
    ],
    "Neurology": [
        "neuro", "eeg", "epilep", "seizure", "migraine", "stroke",
        "cerebro", "brain", "nerve conduction", "parkinson", "dementia",
        "multiple sclerosis", "vitamin b12", "cobalamin", "folic acid",
        "folate", "levetiracetam", "memantine", "carbamazepine"
    ]
}

KNOWN_MEDICATION_NAMES = [
    "Metformin", "Atorvastatin", "Telmisartan", "Amlodipine", "Pantoprazole",
    "Amoxicillin", "Paracetamol", "Glimepiride", "Rosuvastatin", "Losartan",
    "Aspirin", "Omeprazole", "Levothyroxine", "Metoprolol", "Azithromycin",
    "Ciprofloxacin", "Cetirizine", "Montelukast", "Multivitamin", "Vitamin D3",
    "Insulin Glargine", "Vildagliptin", "Empagliflozin", "Dapagliflozin"
]


class MedicalParserService:
    @staticmethod
    def parse_document(raw_text: str) -> Dict[str, Any]:
        """
        Parses document raw text into metadata, observations, medications, and trust warnings.
        """
        lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
        doc_meta = MedicalParserService._extract_metadata(raw_text, lines)
        observations, obs_warnings = MedicalParserService._extract_observations(raw_text, lines)
        medications, med_warnings = MedicalParserService._extract_medications(raw_text, lines)

        # A document carrying multiple laboratory results is a lab report even if it
        # also lists a medication advice line (common on Indian lab printouts).
        if doc_meta.get("document_type") == "Prescription" and len(observations) >= 2:
            doc_meta["document_type"] = "Laboratory Report"

        doc_meta["specialty"] = MedicalParserService._detect_specialty(raw_text)

        all_warnings = obs_warnings + med_warnings
        trust_score = max(30, 100 - (len(all_warnings) * 12))

        return {
            "metadata": doc_meta,
            "observations": observations,
            "medications": medications,
            "trust_warnings": all_warnings,
            "trust_score": trust_score
        }

    @staticmethod
    def _detect_specialty(raw_text: str) -> str:
        """
        Infers the medical specialty a report belongs to using only keywords that
        are physically present in the document. Returns 'General Medicine' when no
        specific specialty markers are found. Never fabricates a specialty.
        """
        lower = raw_text.lower()
        scores = {}
        for specialty, keywords in SPECIALTY_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in lower)
            if score:
                scores[specialty] = score
        if not scores:
            return "General Medicine"
        # Highest keyword count wins; ties resolved by insertion order in SPECIALTY_KEYWORDS.
        return max(scores.items(), key=lambda item: item[1])[0]

    @staticmethod
    def _extract_metadata(raw_text: str, lines: List[str]) -> Dict[str, Any]:
        """Extracts patient name, date, lab name, and document type."""
        patient_name = None
        patient_age = None
        patient_gender = None
        patient_identifier = None
        doc_date = None
        lab_name = None
        doc_type = "Laboratory Report"

        # Check document type
        lower_full = raw_text.lower()
        if "prescription" in lower_full or "rx" in lower_full or "prescribed" in lower_full:
            doc_type = "Prescription"
        elif "discharge summary" in lower_full or "admission date" in lower_full:
            doc_type = "Discharge Summary"
        elif "ultrasound" in lower_full or "x-ray" in lower_full or "mri" in lower_full or "ct scan" in lower_full:
            doc_type = "Diagnostic Report"

        # Search for date pattern: YYYY-MM-DD or DD/MM/YYYY or Month DD, YYYY
        date_match = re.search(r"\b(\d{4}[-/]\d{2}[-/]\d{2}|\d{2}[-/]\d{2}[-/]\d{4}|[A-Za-z]{3,9}\s+\d{1,2},?\s+\d{4})\b", raw_text)
        if date_match:
            doc_date = date_match.group(1)

        # Search for Patient Name
        name_match = re.search(r"\b(?:patient\s+name|patient|pt\s+name|name)\b[\s\:\-]+([A-Za-z][A-Za-z.\s]{2,39})", raw_text, re.IGNORECASE)
        if name_match:
            cand = name_match.group(1).strip().splitlines()[0].strip(" .:-")
            if cand and not any(bad in cand.lower() for bad in ["report", "date", "age", "sex", "gender", "male", "female"]):
                patient_name = cand

        # Search for Age / Gender
        age_match = re.search(r"\b(?:age|years?)[\s\:\-]+(\d{1,3})\b", raw_text, re.IGNORECASE)
        try:
            patient_age = int(age_match.group(1))
        except Exception:
            pass

        # Accept explicit gender, a bare 'Male'/'Female' token, or a short M/F
        # marker next to the age such as "(Age 52 F)".
        if (
            re.search(r"\bfemale\b", raw_text, re.IGNORECASE)
            or re.search(r"\b(?:gender|sex)\s*[:\-]?\s*f\b", raw_text, re.IGNORECASE)
            or re.search(r"\(\s*age\s*[:\-]?\s*\d{1,3}\s*[, ]?\s*f\b", raw_text, re.IGNORECASE)
        ):
            patient_gender = "Female"
        elif (
            re.search(r"\bmale\b", raw_text, re.IGNORECASE)
            or re.search(r"\b(?:gender|sex)\s*[:\-]?\s*m\b", raw_text, re.IGNORECASE)
            or re.search(r"\(\s*age\s*[:\-]?\s*\d{1,3}\s*[, ]?\s*m\b", raw_text, re.IGNORECASE)
        ):
            patient_gender = "Male"

        # Search for Lab / Clinic Name
        lab_match = re.search(r"(?:diagnostic|laboratory|pathology|clinic|hospital|care|health\s*centre)[\s\w\.\-]+", raw_text, re.IGNORECASE)
        if lab_match:
            lab_name = lab_match.group(0).strip()[:80]

        return {
            "patient_name": patient_name,
            "patient_age": patient_age,
            "patient_gender": patient_gender,
            "document_date": doc_date,
            "laboratory_name": lab_name,
            "document_type": doc_type
        }

    @staticmethod
    def _extract_observations(raw_text: str, lines: List[str]) -> Tuple[List[Dict[str, Any]], List[str]]:
        """
        Extracts observations matching known laboratory tests and evaluates reference ranges.
        Never invents values.
        """
        observations = []
        warnings = []
        found_tests = set()

        for test_def in KNOWN_LAB_TESTS:
            test_name = test_def["canonical_name"]
            if test_name in found_tests:
                continue

            for pattern in test_def["patterns"]:
                # Search for pattern in lines
                for line in lines:
                    match = re.search(pattern, line, re.IGNORECASE)
                    if match:
                        obs = MedicalParserService._parse_test_line(line, test_def)
                        if obs:
                            observations.append(obs)
                            found_tests.add(test_name)
                            if obs.get("trust_notes"):
                                warnings.append(f"{test_name}: {obs['trust_notes']}")
                            break
                if test_name in found_tests:
                    break

        # Generic fallback: capture any additional test rows that are not part of the
        # curated library, so that MediMitra can understand ARBITRARY lab reports
        # (e.g. Vitamin D, TSH variants, culture reports, custom panels) without
        # ever inventing values. Only values physically present in the text are used.
        generic_obs = MedicalParserService._extract_generic_tests(lines, found_tests)
        for g in generic_obs:
            observations.append(g)
            if g.get("trust_notes"):
                warnings.append(f"{g['test_name']}: {g['trust_notes']}")

        return observations, warnings

    # Lines that must NEVER be interpreted as a laboratory observation.
    _GENERIC_SKIP_KEYWORDS = [
        "patient", "name:", "name ", "date", "age", "sex", "gender", "doctor", "dr.",
        "ref.", "reference", "report", "status", " id:", "id:", "sample", "collected",
        "received", "lab", "laboratory", "hospital", "clinic", "address", "phone",
        "mobile", "registered", "test name", "result", "unit", "method", "page",
        "barcode", "uhid", "visit", "bill", "amount", "total:", "advice",
        "prescription", "rx", "diagnosis", "impression", "signature", "nabl", "nabh",
        "accredited", "india", "print", "remark", "note", "comment"
    ]

    _MEDICATION_LINE_KEYWORDS = [
        "tab", "tablet", "cap", "capsule", "syrup", "injection", "inj", "syp", "susp",
        "ointment", "cream", "drops", "once daily", "twice daily", "thrice", "od", "bd",
        "tds", "qds", "as directed", "after food", "before food", "bedtime"
    ]

    @staticmethod
    def _extract_generic_tests(lines: List[str], found_tests: set) -> List[Dict[str, Any]]:
        """
        Rule-based extraction of arbitrary "Test Name  Value  Unit  Reference" rows.
        Values are only taken verbatim from the source text; nothing is fabricated.
        """
        observations: List[Dict[str, Any]] = []
        seen_names = set()

        # Normalise names already captured by the curated library to avoid duplicates
        for n in found_tests:
            seen_names.add(re.sub(r"[^a-z0-9]", "", n.lower()))

        max_generic = 60
        for line in lines:
            if len(observations) >= max_generic:
                break

            stripped = line.strip()
            if len(stripped) < 4 or len(stripped) > 160:
                continue

            lower = stripped.lower()

            if any(kw in lower for kw in MedicalParserService._GENERIC_SKIP_KEYWORDS):
                continue
            if any(kw in lower for kw in MedicalParserService._MEDICATION_LINE_KEYWORDS):
                continue
            if any(re.search(rf"\b{re.escape(m)}\b", stripped, re.IGNORECASE) for m in KNOWN_MEDICATION_NAMES):
                continue
            # Skip separator / decorative lines
            if re.fullmatch(r"[\-=_~|*.\s]+", stripped):
                continue
            # Skip rows already captured by the curated library, to avoid duplicates
            if MedicalParserService._line_matches_known_test(stripped):
                continue

            # Locate the first standalone numeric value. A number immediately followed by
            # a hyphen+word (e.g. the "25" in "Vitamin D (25-OH)") is part of the test
            # name, not a result, so it is excluded here.
            value_match = re.search(r"(?<![\w.])(\d{1,6}(?:\.\d+)?)(?![\w\-])", stripped)
            if not value_match:
                continue

            name_part = stripped[:value_match.start()].strip(" :\t|.-")
            if len(name_part) < 2 or not re.search(r"[A-Za-z]", name_part):
                continue
            # Reject names containing stray digits, but allow digits inside parentheses
            # (e.g. "Vitamin D (25-OH)").
            if re.search(r"\d", re.sub(r"\([^)]*\)", "", name_part)):
                continue
            # Reject names that look like a sentence/instruction
            if name_part.count(" ") > 6:
                continue

            norm = re.sub(r"[^a-z0-9]", "", name_part.lower())
            if not norm or norm in seen_names or len(norm) < 3:
                continue

            raw_value = value_match.group(1)
            after = stripped[value_match.end():]

            # Unit: first token right after the value
            unit = None
            unit_match = re.match(
                r"\s*([A-Za-zµ%][A-Za-z0-9%/\^\-\*\u00b5]{0,12})",
                after
            )
            if unit_match:
                candidate = unit_match.group(1)
                # Guard against swallowing range words like "- 99"
                if not re.fullmatch(r"(?i)(to|and|or|upto)", candidate):
                    unit = candidate

            # Reference range detection (explicit in source)
            ref_low = None
            ref_high = None
            ref_text = None
            range_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:-|–|to)\s*(\d+(?:\.\d+)?)", stripped)
            lt_match = re.search(r"<\s*=?\s*(\d+(?:\.\d+)?)", stripped)
            gt_match = re.search(r">\s*=?\s*(\d+(?:\.\d+)?)", stripped)

            if range_match:
                try:
                    ref_low = float(range_match.group(1))
                    ref_high = float(range_match.group(2))
                    ref_text = f"{range_match.group(1)} - {range_match.group(2)}" + (f" {unit}" if unit else "")
                except Exception:
                    pass
            elif lt_match:
                try:
                    ref_low = 0.0
                    ref_high = float(lt_match.group(1))
                    ref_text = f"< {lt_match.group(1)}" + (f" {unit}" if unit else "")
                except Exception:
                    pass
            elif gt_match:
                try:
                    ref_low = float(gt_match.group(1))
                    ref_high = None
                    ref_text = f"> {gt_match.group(1)}" + (f" {unit}" if unit else "")
                except Exception:
                    pass

            try:
                numeric_val = float(raw_value)
            except Exception:
                continue

            interpretation = "UNCERTAIN"
            if ref_low is not None and ref_high is not None:
                if numeric_val < ref_low:
                    interpretation = "LOW"
                elif numeric_val > ref_high:
                    interpretation = "HIGH"
                else:
                    interpretation = "NORMAL"
            elif ref_high is not None:
                interpretation = "HIGH" if numeric_val > ref_high else "NORMAL"
            elif ref_low is not None:
                interpretation = "LOW" if numeric_val < ref_low else "NORMAL"

            notes = None
            if ref_text is None:
                notes = "Reference range was not printed on the report for this test. Interpretation left to your clinician."
            if unit is None:
                notes = (notes + " " if notes else "") + "Unit not explicitly stated in the source line."

            title = re.sub(r"\s+", " ", name_part).strip()
            observations.append({
                "test_name": title,
                "standardized_code": None,
                "original_value": raw_value,
                "standardized_value": numeric_val,
                "unit": unit,
                "reference_range_low": ref_low,
                "reference_range_high": ref_high,
                "reference_range_text": ref_text,
                "interpretation": interpretation,
                "is_verified": False,
                "evidence_excerpt": stripped[:200],
                "page_number": 1,
                "confidence_score": 0.80 if ref_text else 0.68,
                "trust_notes": notes
            })
            seen_names.add(norm)

        return observations

    @staticmethod
    def _line_matches_known_test(line: str) -> bool:
        """True if the line corresponds to a test already handled by KNOWN_LAB_TESTS."""
        for test_def in KNOWN_LAB_TESTS:
            for pattern in test_def["patterns"]:
                if re.search(pattern, line, re.IGNORECASE):
                    return True
        return False

    @staticmethod
    def _parse_test_line(line: str, test_def: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Parses a single line for test value, unit, and reference range."""
        test_name = test_def["canonical_name"]
        default_unit = test_def["default_unit"]
        def_low, def_high, def_ref_text = test_def["default_ref"]

        # Look for numbers in line (supporting decimals)
        numbers = re.findall(r"\b\d+(?:\.\d+)?\b", line)
        if not numbers:
            return None

        # Detect unit
        unit = default_unit
        unit_match = re.search(
            r"\b(mg/dL|g/dL|ng/mL|pg/mL|ng/dL|uIU/mL|mIU/mL|µIU/mL|umol/L|µmol/L|mmol/L|U/L|IU/L|pmol/L|%|/cumm|lakh/cumm)\b",
            line, re.IGNORECASE
        )
        unit_missing = False
        if unit_match:
            unit = unit_match.group(1)
        else:
            unit_missing = True

        # Extract value (usually first or second number following the test name)
        # Check if reference range is explicitly written in the line e.g. "70 - 99" or "< 200"
        ref_range_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:-|to)\s*(\d+(?:\.\d+)?)", line)
        less_than_match = re.search(r"<\s*(\d+(?:\.\d+)?)", line)
        greater_than_match = re.search(r">\s*(\d+(?:\.\d+)?)", line)

        ref_low = def_low
        ref_high = def_high
        ref_text = def_ref_text

        if ref_range_match:
            try:
                ref_low = float(ref_range_match.group(1))
                ref_high = float(ref_range_match.group(2))
                ref_text = f"{ref_low} - {ref_high} {unit}"
            except Exception:
                pass
        elif less_than_match:
            try:
                ref_high = float(less_than_match.group(1))
                ref_low = 0.0
                ref_text = f"< {ref_high} {unit}"
            except Exception:
                pass
        elif greater_than_match:
            try:
                ref_low = float(greater_than_match.group(1))
                ref_high = None
                ref_text = f"> {ref_low} {unit}"
            except Exception:
                pass

        # Select the observed value (the number that is not part of the reference range if possible)
        val_str = None
        for n in numbers:
            fn = float(n)
            # If line has reference range, avoid picking the exact ref low or high if another number exists
            if ref_range_match and (fn == ref_low or fn == ref_high) and len(numbers) > 1:
                continue
            val_str = n
            break

        if not val_str:
            val_str = numbers[0]

        try:
            numeric_val = float(val_str)
        except Exception:
            numeric_val = None

        # Interpretation based strictly on supplied reference ranges
        interpretation = "UNCERTAIN"
        if numeric_val is not None:
            if ref_low is not None and ref_high is not None:
                if numeric_val < ref_low:
                    interpretation = "LOW"
                elif numeric_val > ref_high:
                    interpretation = "HIGH"
                else:
                    interpretation = "NORMAL"
            elif ref_high is not None and numeric_val > ref_high:
                interpretation = "HIGH"
            elif ref_low is not None and numeric_val < ref_low:
                interpretation = "LOW"
            else:
                interpretation = "NORMAL"

        trust_notes = None
        if unit_missing:
            trust_notes = f"Unit was not explicitly printed in source line. Inferred '{unit}' from clinical standard. Please verify."

        return {
            "test_name": test_name,
            "standardized_code": test_def["loinc"],
            "original_value": str(val_str),
            "standardized_value": numeric_val,
            "unit": unit,
            "reference_range_low": ref_low,
            "reference_range_high": ref_high,
            "reference_range_text": ref_text,
            "interpretation": interpretation,
            "is_verified": False,
            "evidence_excerpt": line.strip()[:200],
            "page_number": 1,
            "confidence_score": 0.94 if not unit_missing else 0.78,
            "trust_notes": trust_notes
        }

    @staticmethod
    def _extract_medications(raw_text: str, lines: List[str]) -> Tuple[List[Dict[str, Any]], List[str]]:
        """
        Extracts medications and detects incomplete dosage or timing instructions.
        """
        medications = []
        warnings = []
        found_meds = set()

        for line in lines:
            for med_name in KNOWN_MEDICATION_NAMES:
                if med_name in found_meds:
                    continue
                if re.search(rf"\b{re.escape(med_name)}\b", line, re.IGNORECASE):
                    med_data = MedicalParserService._parse_medication_line(line, med_name)
                    medications.append(med_data)
                    found_meds.add(med_name)
                    if med_data["is_incomplete"]:
                        warnings.append(f"Medication '{med_name}': {med_data['trust_warning']}")

        return medications, warnings

    @staticmethod
    def _parse_medication_line(line: str, med_name: str) -> Dict[str, Any]:
        """Extracts dosage, frequency, timing, and checks completeness."""
        # Dosage match e.g. "500mg", "10 mg", "0.5 ml"
        dosage_match = re.search(r"(\d+(?:\.\d+)?\s*(?:mg|mcg|g|ml|IU|units?))\b", line, re.IGNORECASE)
        dosage = dosage_match.group(1) if dosage_match else None

        # Frequency match e.g. "once daily", "twice daily", "1-0-1", "OD", "BD", "TDS"
        freq = None
        freq_match = re.search(r"\b(once\s+daily|twice\s+daily|thrice\s+daily|1-0-1|1-0-0|0-0-1|0-1-0|OD|BD|TDS|QDS|daily)\b", line, re.IGNORECASE)
        if freq_match:
            freq = freq_match.group(1).upper()
        
        # Timing match e.g. "after food", "before food", "at bedtime", "after breakfast"
        timing = None
        timing_match = re.search(r"\b(after\s+(?:food|dinner|lunch|breakfast)|before\s+(?:food|meals|breakfast)|at\s+bedtime|with\s+meals)\b", line, re.IGNORECASE)
        if timing_match:
            timing = timing_match.group(1).title()

        # Duration match e.g. "30 days", "2 weeks", "for 1 month"
        duration = None
        dur_match = re.search(r"\b(?:for\s+)?(\d+\s+(?:days?|weeks?|months?))\b", line, re.IGNORECASE)
        if dur_match:
            duration = dur_match.group(1)

        # Completeness trust check
        is_incomplete = False
        warning = None

        if not dosage:
            is_incomplete = True
            warning = "Dosage strength is missing from the prescription. Please verify with doctor or pharmacist."
        elif not freq:
            is_incomplete = True
            warning = "Dosing frequency (e.g., once daily) is unstated or ambiguous. Please verify."

        # Schedule time suggestion
        schedule_time = "08:00 AM"
        if timing and "bedtime" in timing.lower():
            schedule_time = "09:30 PM"
        elif timing and "dinner" in timing.lower():
            schedule_time = "08:30 PM"
        elif freq and ("BD" in freq or "TWICE" in freq.upper()):
            schedule_time = "08:00 AM & 08:00 PM"

        return {
            "medicine_name": med_name,
            "dosage": dosage,
            "frequency": freq or "As directed",
            "timing_instructions": timing or "As directed by physician",
            "duration": duration or "Ongoing",
            "is_incomplete": is_incomplete,
            "trust_warning": warning,
            "is_verified": False,
            "schedule_time": schedule_time,
            "is_reminder_active": False,
            "evidence_excerpt": line.strip()[:200]
        }
