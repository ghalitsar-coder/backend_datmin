"""
Test script untuk Google Gemini 2.0 Flash via OpenRouter
"""
from ai_formatter import AIFormatter
import time

# Initialize formatter
formatter = AIFormatter('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')

# Test text
test_text = """Machine Learning adalah cabang dari Artificial Intelligence yang fokus pada pengembangan algoritma yang dapat belajar dari data. Ada beberapa jenis seperti supervised learning, unsupervised learning, dan reinforcement learning. Machine Learning banyak digunakan dalam berbagai aplikasi seperti image recognition, natural language processing, dan recommendation systems."""

print("=" * 70)
print("Testing Google Gemini 2.0 Flash Experimental via OpenRouter")
print("=" * 70)
print(f"\nOriginal Text ({len(test_text)} chars):")
print(test_text[:150] + "...")
print("\nFormatting dengan AI...")

try:
    start = time.time()
    result = formatter.format_text(test_text, use_cache=False)
    end = time.time()
    
    print(f"\n✅ SUCCESS!")
    print(f"⏱️  Latency: {end-start:.2f} seconds")
    print(f"📦 From Cache: {result['from_cache']}")
    print(f"📝 Formatted Length: {len(result['formatted_text'])} chars")
    print("\n" + "=" * 70)
    print("FORMATTED OUTPUT:")
    print("=" * 70)
    print(result['formatted_text'])
    print("=" * 70)
    
except Exception as e:
    print(f"\n❌ ERROR: {str(e)}")
    import traceback
    traceback.print_exc()
