import os
import torch
import numpy as np
import soundfile as sf
import librosa
from TTS.api import TTS
from googletrans import Translator
import pysrt
from pydub import AudioSegment
from pydub.playback import play
import matplotlib.pyplot as plt
from tqdm import tqdm
import json
import tempfile
import shutil

class VoiceCloner:
    def __init__(self, device="cuda" if torch.cuda.is_available() else "cpu"):
        """
        Initialize the Voice Cloner with TTS and translation capabilities
        
        Args:
            device: Device to run the model on (cuda/cpu)
        """
        self.device = device
        self.translator = Translator()
        
        # Initialize TTS with voice cloning capabilities
        print("Loading TTS model...")
        self.tts = TTS("tts_models/multilingual/multi-dataset/your_tts", progress_bar=False)
        self.tts.to(device)
        
        print(f"TTS model loaded on {device}")
        
    def clone_voice(self, reference_audio_path, text, output_path):
        """
        Clone voice from reference audio and generate speech for given text
        
        Args:
            reference_audio_path: Path to reference audio file
            text: Text to synthesize
            output_path: Path to save the generated audio
        """
        try:
            # Generate speech with cloned voice
            self.tts.tts_to_file(
                text=text,
                speaker_wav=reference_audio_path,
                language="en",
                file_path=output_path
            )
            print(f"Generated audio saved to: {output_path}")
            return True
        except Exception as e:
            print(f"Error in voice cloning: {e}")
            return False
    
    def translate_persian_to_english(self, persian_text):
        """
        Translate Persian text to English
        
        Args:
            persian_text: Persian text to translate
            
        Returns:
            Translated English text
        """
        try:
            translation = self.translator.translate(persian_text, src='fa', dest='en')
            return translation.text
        except Exception as e:
            print(f"Translation error: {e}")
            return persian_text
    
    def extract_audio_from_srt(self, srt_path, reference_audio_path, output_dir):
        """
        Extract audio segments from SRT file and generate cloned voice audio
        
        Args:
            srt_path: Path to SRT subtitle file
            reference_audio_path: Path to reference audio for voice cloning
            output_dir: Directory to save generated audio files
        """
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Load SRT file
        subs = pysrt.open(srt_path)
        
        audio_segments = []
        metadata = []
        
        print(f"Processing {len(subs)} subtitle segments...")
        
        for i, sub in enumerate(tqdm(subs, desc="Processing subtitles")):
            # Translate Persian text to English
            english_text = self.translate_persian_to_english(sub.text)
            
            # Generate audio with cloned voice
            output_path = os.path.join(output_dir, f"segment_{i:04d}.wav")
            
            if self.clone_voice(reference_audio_path, english_text, output_path):
                # Load generated audio
                audio, sr = librosa.load(output_path, sr=None)
                
                # Store metadata
                segment_info = {
                    'index': i,
                    'start_time': sub.start.to_time(),
                    'end_time': sub.end.to_time(),
                    'start_ms': sub.start.ordinal,
                    'end_ms': sub.end.ordinal,
                    'persian_text': sub.text,
                    'english_text': english_text,
                    'audio_path': output_path,
                    'duration_ms': sub.end.ordinal - sub.start.ordinal
                }
                
                audio_segments.append(audio)
                metadata.append(segment_info)
        
        # Save metadata
        metadata_path = os.path.join(output_dir, "metadata.json")
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2, default=str)
        
        return audio_segments, metadata
    
    def create_synchronized_audio(self, audio_segments, metadata, output_path, target_duration=None):
        """
        Create synchronized audio file based on SRT timing
        
        Args:
            audio_segments: List of audio segments
            metadata: List of segment metadata
            output_path: Path to save the final synchronized audio
            target_duration: Target duration in milliseconds (optional)
        """
        if not audio_segments or not metadata:
            print("No audio segments to process")
            return False
        
        # Calculate total duration from SRT
        total_duration_ms = metadata[-1]['end_ms']
        
        # Create silent audio of total duration
        sample_rate = 22050  # Standard sample rate
        total_samples = int(total_duration_ms * sample_rate / 1000)
        synchronized_audio = np.zeros(total_samples)
        
        print("Synchronizing audio segments...")
        
        for i, (audio, meta) in enumerate(tqdm(zip(audio_segments, metadata), desc="Synchronizing")):
            # Calculate start and end positions
            start_sample = int(meta['start_ms'] * sample_rate / 1000)
            end_sample = int(meta['end_ms'] * sample_rate / 1000)
            
            # Resize audio to fit the time slot
            target_length = end_sample - start_sample
            if len(audio) > target_length:
                # Truncate if too long
                audio = audio[:target_length]
            elif len(audio) < target_length:
                # Pad with silence if too short
                padding = np.zeros(target_length - len(audio))
                audio = np.concatenate([audio, padding])
            
            # Place audio in the correct position
            synchronized_audio[start_sample:end_sample] = audio
        
        # Save synchronized audio
        sf.write(output_path, synchronized_audio, sample_rate)
        print(f"Synchronized audio saved to: {output_path}")
        
        return True
    
    def process_complete_pipeline(self, persian_audio_path, srt_path, reference_voice_path, output_dir):
        """
        Complete pipeline: Extract audio from SRT, translate, clone voice, and synchronize
        
        Args:
            persian_audio_path: Path to original Persian audio file
            srt_path: Path to SRT subtitle file
            reference_voice_path: Path to reference voice for cloning
            output_dir: Output directory for all generated files
        """
        print("Starting complete voice cloning and translation pipeline...")
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Step 1: Extract and process SRT file
        print("\nStep 1: Processing SRT file and translating...")
        audio_segments, metadata = self.extract_audio_from_srt(srt_path, reference_voice_path, output_dir)
        
        # Step 2: Create synchronized audio
        print("\nStep 2: Creating synchronized audio...")
        synchronized_path = os.path.join(output_dir, "synchronized_english_audio.wav")
        success = self.create_synchronized_audio(audio_segments, metadata, synchronized_path)
        
        if success:
            print(f"\nPipeline completed successfully!")
            print(f"Output directory: {output_dir}")
            print(f"Synchronized audio: {synchronized_path}")
            print(f"Metadata: {os.path.join(output_dir, 'metadata.json')}")
            
            # Create a summary report
            self.create_summary_report(metadata, output_dir)
        else:
            print("Pipeline failed!")
        
        return success
    
    def create_summary_report(self, metadata, output_dir):
        """
        Create a summary report of the processing
        """
        report_path = os.path.join(output_dir, "summary_report.txt")
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("Voice Cloning and Translation Summary Report\n")
            f.write("=" * 50 + "\n\n")
            
            f.write(f"Total segments processed: {len(metadata)}\n")
            f.write(f"Total duration: {metadata[-1]['end_ms'] / 1000:.2f} seconds\n\n")
            
            f.write("Sample translations:\n")
            f.write("-" * 30 + "\n")
            
            for i, meta in enumerate(metadata[:5]):  # Show first 5 translations
                f.write(f"Segment {i+1}:\n")
                f.write(f"  Persian: {meta['persian_text']}\n")
                f.write(f"  English: {meta['english_text']}\n")
                f.write(f"  Duration: {meta['duration_ms']}ms\n\n")
            
            if len(metadata) > 5:
                f.write(f"... and {len(metadata) - 5} more segments\n")
        
        print(f"Summary report saved to: {report_path}")

def main():
    """
    Example usage of the VoiceCloner
    """
    # Initialize the voice cloner
    cloner = VoiceCloner()
    
    # Example usage
    print("Voice Cloner initialized successfully!")
    print("Use the following methods:")
    print("1. clone_voice(reference_audio, text, output_path)")
    print("2. translate_persian_to_english(persian_text)")
    print("3. process_complete_pipeline(persian_audio, srt_file, reference_voice, output_dir)")

if __name__ == "__main__":
    main()