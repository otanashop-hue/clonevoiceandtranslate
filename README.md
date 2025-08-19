# Voice Cloning and Translation Project
# پروژه کلون کردن صدا و ترجمه

A comprehensive tool for voice cloning, Persian to English translation, and synchronized audio generation based on SRT subtitle files.

ابزاری جامع برای کلون کردن صدا، ترجمه فارسی به انگلیسی و تولید فایل صوتی همزمان شده بر اساس فایل‌های زیرنویس SRT.

## Features / ویژگی‌ها

- 🎤 **Voice Cloning**: Clone your voice using Coqui TTS
- 🌐 **Persian to English Translation**: Automatic translation using Google Translate
- 📝 **SRT Processing**: Read and process subtitle files with timing information
- ⏱️ **Audio Synchronization**: Generate synchronized English audio based on SRT timing
- 📊 **Detailed Reports**: Generate comprehensive processing reports

## Installation / نصب

### Prerequisites / پیش‌نیازها

- Python 3.8 or higher
- FFmpeg (for audio processing)
- CUDA (optional, for GPU acceleration)

### Setup / راه‌اندازی

1. **Clone the repository:**
```bash
git clone <repository-url>
cd voice-cloning-project
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Install FFmpeg (if not already installed):**
```bash
# Ubuntu/Debian
sudo apt update && sudo apt install ffmpeg

# macOS
brew install ffmpeg

# Windows
# Download from https://ffmpeg.org/download.html
```

## Usage / استفاده

### Quick Start / شروع سریع

1. **Create a sample SRT file:**
```bash
python srt_utils.py
```

2. **Run the complete pipeline:**
```bash
python main.py --mode complete --srt sample.srt --reference-voice your_voice.wav --output output_directory
```

### Command Line Options / گزینه‌های خط فرمان

#### Complete Pipeline / خط کامل پردازش
```bash
python main.py --mode complete --srt input.srt --reference-voice voice.wav --output output_dir
```

#### Translation Only / فقط ترجمه
```bash
python main.py --mode translate --text "سلام دنیا"
```

#### Voice Cloning Only / فقط کلون کردن صدا
```bash
python main.py --mode clone --reference-voice voice.wav --text "Hello world" --output output.wav
```

### Parameters / پارامترها

- `--mode`: Operation mode (`complete`, `translate`, `clone`)
- `--srt`: Path to SRT subtitle file
- `--reference-voice`: Path to reference voice file for cloning
- `--output`: Output directory or file path
- `--text`: Persian text to translate (for translate mode)
- `--device`: Device to use (`cuda`, `cpu`, `auto`)
- `--verbose`: Enable verbose output

## File Formats / فرمت‌های فایل

### Supported Audio Formats / فرمت‌های صوتی پشتیبانی شده
- WAV
- MP3
- FLAC
- M4A
- OGG

### SRT File Format / فرمت فایل SRT
```
1
00:00:01,000 --> 00:00:04,000
سلام، این یک نمونه متن فارسی است

2
00:00:04,500 --> 00:00:08,000
امیدوارم که این پروژه برای شما مفید باشد
```

## Output Structure / ساختار خروجی

After running the complete pipeline, you'll get:

```
output_directory/
├── synchronized_english_audio.wav    # Final synchronized audio
├── metadata.json                     # Processing metadata
├── summary_report.txt               # Summary report
└── segment_XXXX.wav                 # Individual audio segments
```

## API Usage / استفاده از API

### Basic Usage / استفاده پایه

```python
from voice_cloner import VoiceCloner

# Initialize the voice cloner
cloner = VoiceCloner()

# Translate Persian text
english_text = cloner.translate_persian_to_english("سلام دنیا")
print(english_text)  # Output: Hello world

# Clone voice
cloner.clone_voice("reference.wav", "Hello world", "output.wav")

# Complete pipeline
cloner.process_complete_pipeline(
    persian_audio_path="input.wav",
    srt_path="subtitles.srt", 
    reference_voice_path="voice.wav",
    output_dir="output"
)
```

### SRT Processing / پردازش SRT

```python
from srt_utils import SRTProcessor

processor = SRTProcessor()

# Validate SRT file
is_valid = processor.validate_srt_file("subtitles.srt")

# Analyze timing
analysis = processor.analyze_srt_timing("subtitles.srt")

# Create sample SRT
processor.create_sample_srt("sample.srt")
```

## Troubleshooting / عیب‌یابی

### Common Issues / مشکلات رایج

1. **CUDA out of memory:**
   - Use `--device cpu` to run on CPU
   - Reduce batch size in voice_cloner.py

2. **Translation errors:**
   - Check internet connection
   - Verify Persian text encoding (UTF-8)

3. **Audio format issues:**
   - Ensure FFmpeg is installed
   - Convert audio to WAV format if needed

4. **SRT file errors:**
   - Use `srt_utils.py` to validate SRT format
   - Check timing consistency

### Performance Tips / نکات عملکرد

- Use GPU (CUDA) for faster processing
- Process shorter audio segments for better memory management
- Use high-quality reference voice (clear, no background noise)

## Requirements / نیازمندی‌ها

- Python 3.8+
- PyTorch 2.1.0+
- TTS 0.22.0+
- FFmpeg
- 8GB+ RAM (16GB+ recommended)
- CUDA-compatible GPU (optional but recommended)

## License / مجوز

This project is open source and available under the MIT License.

## Contributing / مشارکت

Contributions are welcome! Please feel free to submit a Pull Request.

## Support / پشتیبانی

For issues and questions, please open an issue on the GitHub repository.

---

**Note / توجه:** This tool is for educational and personal use. Please respect copyright and privacy laws when using voice cloning technology.
