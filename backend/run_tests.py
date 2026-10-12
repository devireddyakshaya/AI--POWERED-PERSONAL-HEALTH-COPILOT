import sys
sys.path.insert(0, r'C:\Users\devir\OneDrive\Desktop\healthsaathi-ai')
sys.path.insert(0, r'C:\Users\devir\OneDrive\Desktop\healthsaathi-ai\backend')

from backend.app.services.ai_service import AIService, is_demo_mode
from backend.app.services.telugu_service import TeluguHealthTranslator
from backend.app.services.multilingual_service import MultilingualHealthExplainer

print('1. is_demo_mode():', is_demo_mode())
print('2. AIService test:')
obs = [{'test_name': 'Fasting Blood Glucose', 'original_value': '142.0', 'unit': 'mg/dL', 'reference_range_text': '70 - 99 mg/dL', 'interpretation': 'HIGH'}]
meds = [{'medicine_name': 'Metformin', 'dosage': '500 mg', 'frequency': 'ONCE DAILY', 'timing_instructions': 'After dinner'}]
s = AIService.generate_health_summary('Test User', 'Laboratory Report', '2025-10-15', obs, meds)
print('   is_demo_generated:', s.get('is_demo_generated'))
print('   english_summary_len:', len(s.get('english_summary', '')))
print('   telugu_summary_len:', len(s.get('telugu_summary', '')))
print('   Has Metformin (en):', 'Metformin' in s.get('english_summary', ''))
print('   Has Metformin (te):', 'Metformin' in s.get('telugu_summary', ''))
print('   Has uncertainty_notes:', 'uncertainty_notes' in s)

print()
print('3. Telugu translator test:')
telugu = TeluguHealthTranslator.generate_telugu_summary('Test User', obs, meds, s['english_summary'])
print('   telugu_length:', len(telugu))
has_telugu = any(0x0C00 <= ord(c) <= 0x0C7F for c in telugu)
print('   Has Telugu script:', has_telugu)
print('   Has Metformin:', 'Metformin' in telugu)
print('   Has 142.0:', '142.0' in telugu)
print('   Has mg/dL:', 'mg/dL' in telugu)
print('   Has 70 - 99:', '70 - 99' in telugu)

print()
print('4. Multilingual test:')
observations = [
    {'test_name': 'Fasting Blood Glucose', 'original_value': '142.0', 'unit': 'mg/dL', 'reference_range_text': '70 - 99 mg/dL', 'interpretation': 'HIGH'},
    {'test_name': 'Serum Creatinine', 'original_value': '1.05', 'unit': 'mg/dL', 'reference_range_text': '0.7 - 1.3 mg/dL', 'interpretation': 'NORMAL'},
]
medications = [{'medicine_name': 'Metformin', 'dosage': '500 mg', 'frequency': 'ONCE DAILY', 'timing_instructions': 'After dinner'}]
for lang in ['en', 'te', 'hi', 'ta', 'kn', 'ml']:
    result = MultilingualHealthExplainer.build(lang, 'Test User', 'Laboratory Report', '2026-01-15', observations, medications)
    print('   ' + lang + ': lang=' + result['language'] + ', summary_len=' + str(len(result['summary'])) + ', findings=' + str(len(result['key_findings'])) + ', questions=' + str(len(result['questions_for_doctor'])))