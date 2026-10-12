/**
 * Patient-friendly explanations for medical laboratory test terminology.
 * Translates complex clinical acronyms into simple everyday English and natural Telugu.
 */

export interface TestGlossaryEntry {
  canonicalName: string;
  simpleEnglish: string;
  telugu: string;
  combinedBracket: string;
  plainDescription: string;
  teluguDescription: string;
}

export const MEDICAL_GLOSSARY: Record<string, TestGlossaryEntry> = {
  hba1c: {
    canonicalName: "HbA1c (Glycated Hemoglobin)",
    simpleEnglish: "3-Month Average Blood Sugar",
    telugu: "గత 3 నెలల సగటు రక్త చక్కెర",
    combinedBracket: "[3-Month Average Blood Sugar / గత 3 నెలల సగటు రక్త చక్కెర]",
    plainDescription: "Shows your average blood sugar level over the past 2 to 3 months, unlike daily finger-prick tests.",
    teluguDescription: "ఇది రోజువారీ పరీక్షలలా కాకుండా, గత 2 నుండి 3 నెలల్లో మీ రక్తంలో చక్కెర సగటును ఖచ్చితంగా తెలియజేస్తుంది."
  },
  glucose: {
    canonicalName: "Fasting Blood Glucose",
    simpleEnglish: "Empty Stomach Blood Sugar",
    telugu: "పరగడుపున రక్త చక్కెర",
    combinedBracket: "[Empty Stomach Blood Sugar / పరగడుపున రక్త చక్కెర]",
    plainDescription: "Measures blood sugar after at least 8 to 10 hours of fasting overnight.",
    teluguDescription: "రాత్రంతా కనీసం 8-10 గంటల ఉపవాసం తర్వాత రక్తంలోని చక్కెర స్థాయిని కొలుస్తుంది."
  },
  cholesterol: {
    canonicalName: "Total Cholesterol",
    simpleEnglish: "Total Blood Fat Level",
    telugu: "రక్తంలో మొత్తం కొవ్వు స్థాయి",
    combinedBracket: "[Total Blood Fat Level / రక్తంలో మొత్తం కొవ్వు స్థాయి]",
    plainDescription: "Measures all circulating cholesterol fats to assess heart health risk.",
    teluguDescription: "గుండె ఆరోగ్యాన్ని అంచనా వేయడానికి రక్తంలో ప్రసరించే కొలెస్ట్రాల్ కొవ్వుల పరిమాణాన్ని తెలియజేస్తుంది."
  },
  triglycerides: {
    canonicalName: "Triglycerides",
    simpleEnglish: "Circulating Blood Fat Calories",
    telugu: "రక్తంలోని కొవ్వు కణాలు",
    combinedBracket: "[Circulating Blood Fat / రక్తంలోని కొవ్వు కణాలు]",
    plainDescription: "Unused calories from food converted into fat stored in your blood.",
    teluguDescription: "మనం తిన్న ఆహారంలో మిగిలిపోయిన క్యాలరీలు కొవ్వుగా మారి రక్తంలో ఉండే స్థాయి."
  },
  hdl: {
    canonicalName: "HDL Cholesterol",
    simpleEnglish: "Good Heart-Protective Fat",
    telugu: "మంచి కొలెస్ట్రాల్ (గుండెకు మేలు చేసేది)",
    combinedBracket: "[Good Heart-Protective Fat / మంచి కొలెస్ట్రాల్]",
    plainDescription: "Carries excess bad cholesterol away from arteries back to the liver.",
    teluguDescription: "ధమనుల నుండి చెడు కొలెస్ట్రాల్‌ను తొలగించి గుండెను రక్షించే మంచి కొవ్వు."
  },
  ldl: {
    canonicalName: "LDL Cholesterol",
    simpleEnglish: "Bad Artery-Clogging Fat",
    telugu: "చెడు కొలెస్ట్రాల్ (రక్తనాళాల్లో పేరుకుపోయేది)",
    combinedBracket: "[Bad Artery Fat / చెడు కొలెస్ట్రాల్]",
    plainDescription: "Too much can build up fatty plaques inside blood vessels.",
    teluguDescription: "ఇది ఎక్కువైతే రక్తనాళాల్లో పేరుకుపోయి రక్త ప్రసరణకు ఆటంకం కలిగించవచ్చు."
  },
  creatinine: {
    canonicalName: "Serum Creatinine",
    simpleEnglish: "Kidney Filtration Indicator",
    telugu: "కిడ్నీ పనితీరును తెలిపే సూచిక",
    combinedBracket: "[Kidney Filtration Health / కిడ్నీ పనితీరు సూచిక]",
    plainDescription: "A waste product from muscle breakdown filtered out by healthy kidneys.",
    teluguDescription: "కండరాల నుండి వెలువడే వ్యర్థం; కిడ్నీలు రక్తాన్ని ఎంత బాగా శుద్ధి చేస్తున్నాయో తెలుపుతుంది."
  },
  bun: {
    canonicalName: "Blood Urea Nitrogen (BUN)",
    simpleEnglish: "Kidney Waste Breakdown Indicator",
    telugu: "కిడ్నీ వ్యర్థాల సూచిక (యూరియా)",
    combinedBracket: "[Kidney Waste Indicator / కిడ్నీ వ్యర్థాల సూచిక]",
    plainDescription: "Shows how well your kidneys and liver handle protein waste.",
    teluguDescription: "కాలేయం మరియు మూత్రపిండాలు ప్రోటీన్ వ్యర్థాలను ఎలా తొలగిస్తున్నాయో సూచిస్తుంది."
  },
  hemoglobin: {
    canonicalName: "Hemoglobin (Hb)",
    simpleEnglish: "Blood Oxygen Carrier / Blood Count",
    telugu: "రక్త పరిమాణం / ఆక్సిజన్ మోసే రక్తం శాతం",
    combinedBracket: "[Blood Oxygen Carrier / రక్తం శాతం]",
    plainDescription: "The iron-rich protein in red blood cells that delivers oxygen throughout your body.",
    teluguDescription: "శరీరంలోని అన్ని భాగాలకు ఆక్సిజన్‌ను మోసుకెళ్లే ఎర్ర రక్త కణాల ప్రోటీన్."
  },
  wbc: {
    canonicalName: "Total Leukocyte Count (WBC)",
    simpleEnglish: "Infection-Fighting White Cells",
    telugu: "వ్యాధి నిరోధక తెల్ల రక్త కణాలు",
    combinedBracket: "[Immune Defense Cells / తెల్ల రక్త కణాలు]",
    plainDescription: "Your immune system's defensive cells that fight off bacteria and viral infections.",
    teluguDescription: "ఇన్‌ఫెక్షన్లు మరియు వ్యాధులతో పోరాడే రోగనిరోధక రక్షణ కణాలు."
  },
  platelets: {
    canonicalName: "Platelet Count",
    simpleEnglish: "Blood Clotting Cells",
    telugu: "రక్తం గడ్డకట్టించే కణాలు",
    combinedBracket: "[Blood Clotting Cells / రక్తం గడ్డకట్టించే కణాలు]",
    plainDescription: "Tiny blood cells that clump together to stop bleeding when you have an injury.",
    teluguDescription: "గాయాలు అయినప్పుడు అధిక రక్తస్రావం కాకుండా రక్తాన్ని గడ్డకట్టించే కణాలు."
  },
  tsh: {
    canonicalName: "Thyroid Stimulating Hormone (TSH)",
    simpleEnglish: "Thyroid Gland Metabolism Regulator",
    telugu: "థైరాయిడ్ గ్రంథి పనితీరు నియంత్రిక",
    combinedBracket: "[Thyroid Health Regulator / థైరాయిడ్ పనితీరు]",
    plainDescription: "A master hormone that regulates body metabolism, energy levels, and weight.",
    teluguDescription: "శరీర జీవక్రియలు, శక్తి మరియు బరువును నియంత్రించే థైరాయిడ్ హార్మోన్."
  },
  sgpt: {
    canonicalName: "SGPT / ALT",
    simpleEnglish: "Liver Health Enzyme",
    telugu: "కాలేయ ఆరోగ్య ఎంజైమ్",
    combinedBracket: "[Liver Health Enzyme / కాలేయ పనితీరు]",
    plainDescription: "An enzyme found mainly in liver cells; elevated levels indicate liver cell irritation.",
    teluguDescription: "కాలేయ కణాలలో ఉండే ఎంజైమ్; దీని స్థాయి కాలేయ ఆరోగ్యాన్ని సూచిస్తుంది."
  },
  uric_acid: {
    canonicalName: "Serum Uric Acid",
    simpleEnglish: "Joint & Gout Waste Byproduct",
    telugu: "కీళ్ల నొప్పుల వ్యర్థ పదార్థం (యూరిక్ యాసిడ్)",
    combinedBracket: "[Joint & Gout Marker / కీళ్ల నొప్పుల వ్యర్థం]",
    plainDescription: "High levels can form painful crystals in joints, commonly in the big toe (gout).",
    teluguDescription: "రక్తంలో ఇది పెరిగితే కీళ్లలో స్పటికాలుగా మారి తీవ్రమైన కీళ్ల నొప్పులకు దారితీయవచ్చు."
  }
};

/**
 * Returns bracketed simple English and Telugu description for a test name
 */
export function getFriendlyTestSubtitle(testName: string, lang: 'en' | 'te' | 'both' = 'both'): string {
  const clean = testName.toLowerCase();
  
  let entry: TestGlossaryEntry | undefined;
  if (clean.includes('hba1c') || clean.includes('glycated')) entry = MEDICAL_GLOSSARY.hba1c;
  else if (clean.includes('glucose') || clean.includes('sugar') || clean.includes('fbs')) entry = MEDICAL_GLOSSARY.glucose;
  else if (clean.includes('creatinine')) entry = MEDICAL_GLOSSARY.creatinine;
  else if (clean.includes('triglyceride')) entry = MEDICAL_GLOSSARY.triglycerides;
  else if (clean.includes('hdl')) entry = MEDICAL_GLOSSARY.hdl;
  else if (clean.includes('ldl')) entry = MEDICAL_GLOSSARY.ldl;
  else if (clean.includes('cholesterol')) entry = MEDICAL_GLOSSARY.cholesterol;
  else if (clean.includes('hemoglobin') || clean.includes('haemoglobin') || clean.includes('hb')) entry = MEDICAL_GLOSSARY.hemoglobin;
  else if (clean.includes('wbc') || clean.includes('leukocyte') || clean.includes('tlc')) entry = MEDICAL_GLOSSARY.wbc;
  else if (clean.includes('platelet')) entry = MEDICAL_GLOSSARY.platelets;
  else if (clean.includes('tsh') || clean.includes('thyroid')) entry = MEDICAL_GLOSSARY.tsh;
  else if (clean.includes('sgpt') || clean.includes('alt')) entry = MEDICAL_GLOSSARY.sgpt;
  else if (clean.includes('uric')) entry = MEDICAL_GLOSSARY.uric_acid;
  else if (clean.includes('urea') || clean.includes('bun')) entry = MEDICAL_GLOSSARY.bun;

  if (!entry) return '';

  if (lang === 'en') return `[${entry.simpleEnglish}]`;
  if (lang === 'te') return `[${entry.telugu}]`;
  return entry.combinedBracket;
}
