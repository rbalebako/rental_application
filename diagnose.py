#!/usr/bin/env python3
"""Diagnose Python environment and package installation."""

import sys
import subprocess

print("=" * 60)
print("PYTHON ENVIRONMENT DIAGNOSIS")
print("=" * 60)

print(f"\n1. Python executable: {sys.executable}")
print(f"2. Python version: {sys.version}")
print(f"3. Python path:")
for p in sys.path:
    print(f"   - {p}")

print("\n4. Checking installed packages:")
packages = ["pdfplumber", "pypdf", "pydantic", "pytest", "requests"]
for pkg in packages:
    try:
        mod = __import__(pkg)
        location = getattr(mod, "__file__", "unknown")
        print(f"   ✓ {pkg}: {location}")
    except ImportError:
        print(f"   ✗ {pkg}: NOT INSTALLED")

print("\n5. Pip location:")
result = subprocess.run([sys.executable, "-m", "pip", "show", "pdfplumber"],
                       capture_output=True, text=True)
print(result.stdout if result.returncode == 0 else "pdfplumber not found")

print("\n6. Running pip list:")
result = subprocess.run([sys.executable, "-m", "pip", "list"],
                       capture_output=True, text=True)
print(result.stdout[:500] + "...")
