"""
Standalone Python Test Runner for MediMitra AI Backend.
Executes pytest programmatically or runs direct workflow tests.
"""
import sys
import subprocess
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

def main():
    print("=" * 70)
    print("  MediMitra AI — Automated Backend Verification Suite")
    print("=" * 70)

    try:
        import pytest
        test_file = Path(__file__).resolve().parent / "test_api.py"
        print(f"Running pytest on: {test_file}\n")
        exit_code = pytest.main(["-v", "-o", f"pythonpath={PROJECT_ROOT}", str(test_file)])
        if exit_code == 0:
            print("\n[SUCCESS] All MediMitra AI test cases passed!")
        else:
            print(f"\n[WARNING] Some test cases exited with status code: {exit_code}")
        return exit_code
    except ImportError:
        print("[NOTE] pytest is not yet installed in this environment.")
        print("To run tests: pip install pytest httpx && pytest backend/tests/test_api.py")
        return 0

if __name__ == "__main__":
    sys.exit(main())
