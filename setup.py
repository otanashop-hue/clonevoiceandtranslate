#!/usr/bin/env python3
"""
Setup script for Voice Cloning Project
اسکریپت راه‌اندازی برای پروژه کلون کردن صدا
"""

import os
import sys
import subprocess
import platform

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    else:
        print(f"✅ Python version: {sys.version}")
        return True

def install_ffmpeg():
    """Install FFmpeg based on the operating system"""
    system = platform.system().lower()
    
    print(f"Detected OS: {system}")
    
    if system == "linux":
        print("Installing FFmpeg on Linux...")
        try:
            subprocess.run(["sudo", "apt", "update"], check=True)
            subprocess.run(["sudo", "apt", "install", "-y", "ffmpeg"], check=True)
            print("✅ FFmpeg installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install FFmpeg: {e}")
            return False
    
    elif system == "darwin":  # macOS
        print("Installing FFmpeg on macOS...")
        try:
            subprocess.run(["brew", "install", "ffmpeg"], check=True)
            print("✅ FFmpeg installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install FFmpeg: {e}")
            print("Please install Homebrew first: https://brew.sh/")
            return False
    
    elif system == "windows":
        print("⚠️  FFmpeg installation on Windows requires manual setup")
        print("Please download FFmpeg from: https://ffmpeg.org/download.html")
        print("And add it to your PATH environment variable")
        return False
    
    else:
        print(f"⚠️  Unsupported operating system: {system}")
        return False

def install_python_dependencies():
    """Install Python dependencies"""
    print("Installing Python dependencies...")
    
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], check=True)
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        print("✅ Python dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install Python dependencies: {e}")
        return False

def create_directories():
    """Create necessary directories"""
    directories = ["output", "temp", "models"]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Created directory: {directory}")

def run_tests():
    """Run installation tests"""
    print("Running installation tests...")
    
    try:
        result = subprocess.run([sys.executable, "test_installation.py"], 
                              capture_output=True, text=True, timeout=60)
        print(result.stdout)
        if result.stderr:
            print("Warnings/Errors:", result.stderr)
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print("❌ Tests timed out")
        return False
    except Exception as e:
        print(f"❌ Failed to run tests: {e}")
        return False

def main():
    """Main setup function"""
    print("Voice Cloning Project - Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install FFmpeg
    print("\nChecking FFmpeg installation...")
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        print("✅ FFmpeg is already installed")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("FFmpeg not found, attempting to install...")
        if not install_ffmpeg():
            print("⚠️  FFmpeg installation failed. Please install manually.")
    
    # Install Python dependencies
    print("\nInstalling Python dependencies...")
    if not install_python_dependencies():
        print("❌ Failed to install dependencies")
        sys.exit(1)
    
    # Create directories
    print("\nCreating directories...")
    create_directories()
    
    # Run tests
    print("\nRunning installation tests...")
    if run_tests():
        print("\n🎉 Setup completed successfully!")
        print("\nNext steps:")
        print("1. Run demo: python example.py")
        print("2. Test voice cloning: python main.py --mode clone --reference-voice your_voice.wav --text 'Hello' --output test.wav")
        print("3. Run complete pipeline: python main.py --mode complete --srt demo.srt --reference-voice your_voice.wav --output output_dir")
    else:
        print("\n⚠️  Setup completed with warnings. Some features may not work properly.")
        print("Please check the test output above for details.")

if __name__ == "__main__":
    main()