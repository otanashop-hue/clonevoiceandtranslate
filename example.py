#!/usr/bin/env python3
"""
Example usage of the Voice Cloning and Translation Project
نمونه استفاده از پروژه کلون کردن صدا و ترجمه
"""

import os
import tempfile
from voice_cloner import VoiceCloner
from srt_utils import SRTProcessor

def create_demo_files():
    """Create demo files for testing"""
    print("Creating demo files...")
    
    # Create sample SRT file
    processor = SRTProcessor()
    processor.create_sample_srt("demo.srt")
    
    # Create a simple text file with Persian text
    persian_text = """سلام، این یک نمونه متن فارسی است.
امیدوارم که این پروژه برای شما مفید باشد.
این سیستم می‌تواند صدا را کلون کند و متن را ترجمه کند."""
    
    with open("demo_text.txt", "w", encoding="utf-8") as f:
        f.write(persian_text)
    
    print("✅ Demo files created: demo.srt, demo_text.txt")

def demo_translation():
    """Demonstrate translation functionality"""
    print("\n" + "="*50)
    print("DEMO: Persian to English Translation")
    print("="*50)
    
    cloner = VoiceCloner()
    
    # Read demo text
    with open("demo_text.txt", "r", encoding="utf-8") as f:
        persian_text = f.read()
    
    print(f"Persian text: {persian_text}")
    
    # Translate
    english_text = cloner.translate_persian_to_english(persian_text)
    print(f"English translation: {english_text}")

def demo_srt_analysis():
    """Demonstrate SRT analysis"""
    print("\n" + "="*50)
    print("DEMO: SRT File Analysis")
    print("="*50)
    
    processor = SRTProcessor()
    processor.print_srt_analysis("demo.srt")

def demo_voice_cloning():
    """Demonstrate voice cloning (requires reference audio)"""
    print("\n" + "="*50)
    print("DEMO: Voice Cloning")
    print("="*50)
    
    print("Note: This demo requires a reference voice file.")
    print("To test voice cloning, you need to provide a WAV file with your voice.")
    print("\nExample usage:")
    print("python main.py --mode clone --reference-voice your_voice.wav --text 'Hello world' --output demo_output.wav")

def demo_complete_pipeline():
    """Demonstrate complete pipeline"""
    print("\n" + "="*50)
    print("DEMO: Complete Pipeline")
    print("="*50)
    
    print("To run the complete pipeline, you need:")
    print("1. A reference voice file (WAV format)")
    print("2. An SRT file with Persian subtitles")
    print("\nExample usage:")
    print("python main.py --mode complete --srt demo.srt --reference-voice your_voice.wav --output demo_output")

def main():
    """Run all demos"""
    print("Voice Cloning Project - Demo")
    print("="*50)
    
    # Create demo files
    create_demo_files()
    
    # Run demos
    demo_translation()
    demo_srt_analysis()
    demo_voice_cloning()
    demo_complete_pipeline()
    
    print("\n" + "="*50)
    print("Demo completed!")
    print("\nNext steps:")
    print("1. Test installation: python test_installation.py")
    print("2. Run voice cloning: python main.py --mode clone --reference-voice your_voice.wav --text 'Hello' --output test.wav")
    print("3. Run complete pipeline: python main.py --mode complete --srt demo.srt --reference-voice your_voice.wav --output output_dir")

if __name__ == "__main__":
    main()