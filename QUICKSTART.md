# Quick Start Guide / راهنمای شروع سریع

## 1. Installation / نصب

### Automatic Setup / نصب خودکار
```bash
python setup.py
```

### Manual Setup / نصب دستی
```bash
# Install dependencies
pip install -r requirements.txt

# Install FFmpeg (Ubuntu/Debian)
sudo apt update && sudo apt install ffmpeg

# Test installation
python test_installation.py
```

## 2. Quick Test / تست سریع

### Create Demo Files / ایجاد فایل‌های نمونه
```bash
python example.py
```

### Test Translation / تست ترجمه
```bash
python main.py --mode translate --text "سلام دنیا"
```

### Test Voice Cloning / تست کلون کردن صدا
```bash
python main.py --mode clone --reference-voice your_voice.wav --text "Hello world" --output test.wav
```

## 3. Complete Pipeline / خط کامل پردازش

### Step 1: Prepare Files / مرحله ۱: آماده‌سازی فایل‌ها
- Create SRT file with Persian subtitles
- Prepare reference voice file (WAV format, clear speech)

### Step 2: Run Pipeline / مرحله ۲: اجرای خط پردازش
```bash
python main.py --mode complete --srt input.srt --reference-voice voice.wav --output output_dir
```

### Step 3: Check Results / مرحله ۳: بررسی نتایج
- `output_dir/synchronized_english_audio.wav` - Final audio
- `output_dir/metadata.json` - Processing details
- `output_dir/summary_report.txt` - Summary report

## 4. File Requirements / نیازمندی‌های فایل

### Reference Voice / صدای مرجع
- Format: WAV (recommended), MP3, FLAC
- Duration: 10-30 seconds
- Quality: Clear speech, no background noise
- Content: Natural speech in any language

### SRT File / فایل SRT
```
1
00:00:01,000 --> 00:00:04,000
سلام، این یک نمونه متن فارسی است

2
00:00:04,500 --> 00:00:08,000
امیدوارم که این پروژه برای شما مفید باشد
```

## 5. Troubleshooting / عیب‌یابی

### Common Issues / مشکلات رایج

**CUDA out of memory:**
```bash
python main.py --mode complete --device cpu --srt input.srt --reference-voice voice.wav --output output_dir
```

**Translation fails:**
- Check internet connection
- Verify Persian text encoding (UTF-8)

**Audio quality issues:**
- Use high-quality reference voice
- Ensure FFmpeg is installed
- Convert audio to WAV format

## 6. Performance Tips / نکات عملکرد

- Use GPU (CUDA) for faster processing
- Process shorter segments for better memory management
- Use clear, high-quality reference voice
- Close other applications during processing

## 7. Example Workflow / نمونه گردش کار

```bash
# 1. Setup
python setup.py

# 2. Test installation
python test_installation.py

# 3. Create demo files
python example.py

# 4. Run complete pipeline
python main.py --mode complete --srt demo.srt --reference-voice your_voice.wav --output my_output

# 5. Check results
ls my_output/
cat my_output/summary_report.txt
```

## 8. API Usage / استفاده از API

```python
from voice_cloner import VoiceCloner

# Initialize
cloner = VoiceCloner()

# Translate
english = cloner.translate_persian_to_english("سلام دنیا")

# Clone voice
cloner.clone_voice("voice.wav", "Hello world", "output.wav")

# Complete pipeline
cloner.process_complete_pipeline(
    srt_path="input.srt",
    reference_voice_path="voice.wav", 
    output_dir="output"
)
```

---

**Need help?** Check the full README.md for detailed documentation.