#!/usr/bin/env python3
"""
Quick database migration script to update sensor types
Run this after modifying the SensorReading model
"""
import os
import sys
import django

# Setup Django
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
API_PATH = os.path.join(PROJECT_ROOT, 'api')
sys.path.insert(0, API_PATH)
os.chdir(API_PATH)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hypervolt_backend.settings')
django.setup()

import subprocess

print("=" * 60)
print("  HYPERVOLT DATABASE MIGRATION")
print("=" * 60)
print()

print("Creating migrations...")
result = subprocess.run([sys.executable, 'manage.py', 'makemigrations'], cwd=API_PATH)

if result.returncode == 0:
    print("\n✅ Migrations created successfully!")
    print("\nApplying migrations...")
    result = subprocess.run([sys.executable, 'manage.py', 'migrate'], cwd=API_PATH)

    if result.returncode == 0:
        print("\n✅ Migrations applied successfully!")
        print("\nDatabase is now up to date.")
    else:
        print("\n❌ Failed to apply migrations!")
        sys.exit(1)
else:
    print("\n⚠️  No changes detected or error occurred.")
    print("This might be okay if no changes were needed.")

print("\n" + "=" * 60)
print("  You can now run the simulation!")
print("=" * 60)
