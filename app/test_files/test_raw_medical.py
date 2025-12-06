#!/usr/bin/env python3
"""
Test raw medical advice generation
"""

import asyncio
import sys
import os

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.medgemma import get_med_gemma3

async def test_raw_medical():
    """Test raw medical advice generation"""
    try:
        model = get_med_gemma3()
        
        # Test with a direct medical question
        test_query = "I have a headache, what should I do?"
        print(f"Test Query: {test_query}")
        print("=" * 60)
        
        response = await model.generate_raw_medical_advice(test_query)
        print(f"Raw Medical Response:")
        print(response)
        print("=" * 60)
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_raw_medical())
