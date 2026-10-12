import py_compile
import sys

try:
    py_compile.compile(r'C:\Users\devir\OneDrive\Desktop\healthsaathi-ai\backend\agent\ai_telugu_agent.py', doraise=True)
    print('Syntax OK')
    sys.exit(0)
except py_compile.PyCompileError as e:
    print(f'Compile error: {e}')
    sys.exit(1)