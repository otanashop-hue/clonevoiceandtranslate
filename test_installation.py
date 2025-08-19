#!/usr/bin/env python3
"""
Test script to verify installation and dependencies
اسکریپت تست برای بررسی نصب و وابستگی‌ها
"""

import sys
import importlib
import subprocess
import os

def test_import(module_name, package_name=None):
    """Test if a module can be imported"""
    try:
        importlib.import_module(module_name)
        print(f"✅ {package_name or module_name} - OK")
        return True
    except ImportError as e:
        print(f"❌ {package_name or module_name} - FAILED: {e}")
        return False

def test_ffmpeg():
    """Test if FFmpeg is available"""
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ FFmpeg - OK")
            return True
        else:
            print("❌ FFmpeg - FAILED: Command returned non-zero exit code")
            return False
    except FileNotFoundError:
        print("❌ FFmpeg - FAILED: Not found in PATH")
        return False
    except subprocess.TimeoutExpired:
        print("❌ FFmpeg - FAILED: Command timed out")
        return False

def test_cuda():
    """Test if CUDA is available"""
    try:
        import torch
        if torch.cuda.is_available():
            print(f"✅ CUDA - OK (Version: {torch.version.cuda})")
            print(f"   Available GPUs: {torch.cuda.device_count()}")
            return True
        else:
            print("⚠️  CUDA - Not available (will use CPU)")
            return False
    except ImportError:
        print("❌ PyTorch - FAILED: Cannot import torch")
        return False

def test_tts_models():
    """Test TTS model availability"""
    try:
        from TTS.api import TTS
        # List available models
        models = TTS.list_models()
        if models:
            print(f"✅ TTS Models - OK ({len(models)} models available)")
            return True
        else:
            print("⚠️  TTS Models - No models found")
            return False
    except Exception as e:
        print(f"❌ TTS Models - FAILED: {e}")
        return False

def test_srt_processing():
    """Test SRT processing capabilities"""
    try:
        from srt_utils import SRTProcessor
        processor = SRTProcessor()
        processor.create_sample_srt("test_sample.srt")
        
        # Test validation
        is_valid = processor.validate_srt_file("test_sample.srt")
        
        # Clean up
        if os.path.exists("test_sample.srt"):
            os.remove("test_sample.srt")
        
        if is_valid:
            print("✅ SRT Processing - OK")
            return True
        else:
            print("❌ SRT Processing - FAILED: Sample file validation failed")
            return False
    except Exception as e:
        print(f"❌ SRT Processing - FAILED: {e}")
        return False

def test_voice_cloner():
    """Test voice cloner initialization"""
    try:
        from voice_cloner import VoiceCloner
        print("✅ Voice Cloner - OK (Initialization successful)")
        return True
    except Exception as e:
        print(f"❌ Voice Cloner - FAILED: {e}")
        return False

def main():
    """Run all tests"""
    print("Voice Cloning Project - Installation Test")
    print("=" * 50)
    
    tests = [
        ("Python Version", lambda: sys.version_info >= (3, 8)),
        ("PyTorch", lambda: test_import("torch")),
        ("TTS", lambda: test_import("TTS")),
        ("Librosa", lambda: test_import("librosa")),
        ("SoundFile", lambda: test_import("soundfile")),
        ("Pydub", lambda: test_import("pydub")),
        ("Google Translate", lambda: test_import("googletrans")),
        ("PySRT", lambda: test_import("pysrt")),
        ("NumPy", lambda: test_import("numpy")),
        ("Matplotlib", lambda: test_import("matplotlib")),
        ("FFmpeg", test_ffmpeg),
        ("CUDA", test_cuda),
        ("TTS Models", test_tts_models),
        ("SRT Processing", test_srt_processing),
        ("Voice Cloner", test_voice_cloner),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\nTesting {test_name}...")
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ {test_name} - FAILED: {e}")
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your installation is ready.")
        print("\nNext steps:")
        print("1. Create a sample SRT file: python srt_utils.py")
        print("2. Run the complete pipeline: python main.py --mode complete --srt sample.srt --reference-voice your_voice.wav --output output_dir")
    else:
        print("⚠️  Some tests failed. Please check the installation.")
        print("\nCommon solutions:")
        print("1. Install missing packages: pip install -r requirements.txt")
        print("2. Install FFmpeg: sudo apt install ffmpeg (Ubuntu/Debian)")
        print("3. Check CUDA installation if using GPU")

if __name__ == "__main__":
    main()