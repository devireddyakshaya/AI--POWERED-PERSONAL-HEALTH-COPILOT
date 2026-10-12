with open(r'C:\Users\devir\OneDrive\Desktop\healthsaathi-ai\backend\agent\ai_telugu_agent.py', 'rb') as f:
    content = f.read()
# Replace the test_documents_endpoint function's observation check
# Change from checking 'observations' to 'observation_count'
old = b'assert \"observations\" in doc, \"Document missing observations\"'
new = b'assert \"observation_count\" in doc and doc[\"observation_count\"] > 0, \"Document missing observation count\"'
content = content.replace(old, new)
with open(r'C:\Users\devir\OneDrive\Desktop\healthsaathi-ai\backend\agent\ai_telugu_agent.py', 'wb') as f:
    f.write(content)
print('Fixed! Old pattern found:', b'assert "observations"' in content)