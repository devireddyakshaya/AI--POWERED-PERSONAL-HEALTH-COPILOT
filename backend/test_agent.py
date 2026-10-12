import sys
import os
sys.path.insert(0, r'C:\Users\devir\OneDrive\Desktop\healthsaathi-ai')
sys.path.insert(0, r'C:\Users\devir\OneDrive\Desktop\healthsaathi-ai\backend')

# Use project directory for temp files
TMP_DIR = r'C:\Users\devir\OneDrive\Desktop\healthsaathi-ai\backend'
os.makedirs(TMP_DIR, exist_ok=True)

from backend.app.services.telugu_service import TeluguHealthTranslator
from backend.app.services.multilingual_service import MultilingualHealthExplainer

# Test Telugu translator
obs = [
    {'test_name': 'Fasting Blood Glucose', 'original_value': '142.0', 'unit': 'mg/dL', 'reference_range_text': '70 - 99 mg/dL', 'interpretation': 'HIGH'},
    {'test_name': 'Serum Creatinine', 'original_value': '1.05', 'unit': 'mg/dL', 'reference_range_text': '0.7 - 1.3 mg/dL', 'interpretation': 'NORMAL'},
]
meds = [{'medicine_name': 'Metformin', 'dosage': '500 mg', 'frequency': 'ONCE DAILY', 'timing_instructions': 'After dinner'}]

english_summary = 'Hello Test User, here is an easy-to-understand breakdown of your Laboratory Report. Key Findings Requiring Attention:'

telugu = TeluguHealthTranslator.generate_telugu_summary('Test User', obs, meds, english_summary)
with open(os.path.join(TMP_DIR, 'telugu_output.txt'), 'w', encoding='utf-8') as f:
    f.write(telugu)
print('Telugu output written')
print('Length:', len(telugu))

# Check properties without printing Unicode directly
has_telugu_script = any(0x0C00 <= ord(c) <= 0x0C7F for c in telugu)
print('Has Telugu script:', has_telugu_script)
print('Has Metformin:', 'Metformin' in telugu)
print('Has 142.0:', '142.0' in telugu)
print('Has mg/dL:', 'mg/dL' in telugu)
print('Has 70 - 99:', '70 - 99' in telugu)
print('Has disclaimer:', 'గమనిక' in telugu)

# Test multilingual
print()
observations = [
    {'test_name': 'Fasting Blood Glucose', 'original_value': '142.0', 'unit': 'mg/dL', 'reference_range_text': '70 - 99 mg/dL', 'interpretation': 'HIGH'},
    {'test_name': 'Serum Creatinine', 'original_value': '1.05', 'unit': 'mg/dL', 'reference_range_text': '0.7 - 1.3 mg/dL', 'interpretation': 'NORMAL'},
]
medications = [{'medicine_name': 'Metformin', 'dosage': '500 mg', 'frequency': 'ONCE DAILY', 'timing_instructions': 'After dinner'}]

with open(os.path.join(TMP_DIR, 'multilingual_output.txt'), 'w', encoding='utf-8') as f:
    for lang in ['en', 'te', 'hi', 'ta', 'kn', 'ml']:
        result = MultilingualHealthExplainer.build(lang, 'Test User', 'Laboratory Report', '2026-01-15', observations, medications)
        line = f'{lang}: summary_len={len(result["summary"])}, language={result["language"]}, findings={len(result["key_findings"])}, questions={len(result["questions_for_doctor"])}\n'
        f.write(line)
        print(line.strip())
        # Check medicine preserved
        has_142 = '142' in result['summary']
        print(f'  Has numerical value: {has_142}')