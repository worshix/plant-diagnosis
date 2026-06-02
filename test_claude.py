#!/usr/bin/env python3
"""
Test script to see Claude's classification response on your images.
Run this before uploading through Django to verify API is working.
"""

import os
import sys

# Load env variables
from dotenv import load_dotenv
load_dotenv()

from tobaccoclassifier.diagosis.claude_classifier import classify_with_claude

# Test with one of your WhatsApp images
test_images = [
    "WhatsApp Image 2026-06-02 at 02.41.30.jpeg",
    "WhatsApp Image 2026-06-02 at 13.03.42.jpeg",
    "WhatsApp Image 2026-06-02 at 13.03.43.jpeg",
]

# Test conditions
test_conditions = {
    'temperature': 24,
    'humidity': 75,
    'moisture': 45
}

print("=" * 70)
print("CLAUDE VISION API TEST")
print("=" * 70)

api_key = os.environ.get('ANTHROPIC_API_KEY')
if not api_key or api_key == 'your-api-key-here':
    print("\n⚠️  WARNING: No API key found!")
    print("Please add your ANTHROPIC_API_KEY to the .env file")
    print("Get one at: https://console.anthropic.com/")
    sys.exit(1)

print(f"\n✓ API Key found: {api_key[:10]}...")
print(f"\nTest conditions: {test_conditions}")
print("=" * 70)

for img_name in test_images:
    img_path = os.path.join(os.path.dirname(__file__), img_name)
    
    if not os.path.exists(img_path):
        print(f"\n❌ Image not found: {img_name}")
        continue
    
    print(f"\n🔍 Testing: {img_name}")
    print("-" * 70)
    
    try:
        result = classify_with_claude(
            img_path,
            temperature=test_conditions['temperature'],
            humidity=test_conditions['humidity'],
            moisture=test_conditions['moisture']
        )
        
        print(f"Disease:        {result['disease']}")
        print(f"Confidence:     {result['confidence']:.1f}%")
        print(f"Reasoning:      {result['reasoning'][:150]}...")
        print(f"Features:       {result['distinguishing_features'][:100]}...")
        print("✓ Success!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

print("\n" + "=" * 70)
print("Test complete!")
print("=" * 70)
