#!/usr/bin/env python3
"""
Test script to verify all imports work correctly
"""
try:
    import fastmcp
    print("✓ fastmcp imported successfully")
except ImportError as e:
    print(f"✗ fastmcp import failed: {e}")

try:
    import flask
    print("✓ flask imported successfully")
except ImportError as e:
    print(f"✗ flask import failed: {e}")

try:
    import requests
    print("✓ requests imported successfully")
except ImportError as e:
    print(f"✗ requests import failed: {e}")

try:
    import uvicorn
    print("✓ uvicorn imported successfully")
except ImportError as e:
    print(f"✗ uvicorn import failed: {e}")

print("Import test completed!")
