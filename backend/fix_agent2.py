with open(r'C:\Users\devir\OneDrive\Desktop\healthsaathi-ai\backend\agent\ai_telugu_agent.py', 'rb') as f:
    content = f.read()
# Replace the test_documents_endpoint function's medication check
old = b'assert \"medications\" in doc, \"Document missing medications\"'
new = b'assert \"medication_count\" in doc and doc[\"medication_count\"] > 0, \"Document missing medication count\"'
content = content.replace(old, new)
with open(r'C:\Users\devir\OneDrive\Desktop\healthsaathi-ai\backend\agent\ai_telugu_agent.py', 'wb') as f:
    f.write(content)
print('Fixed!' if content != f.read() else 'No change needed')