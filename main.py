#!/usr/bin/env python3
"""
Voice Cloning and Translation CLI
پروژه کلون کردن صدا و ترجمه از فارسی به انگلیسی
"""

import argparse
import os
import sys
from voice_cloner import VoiceCloner

def main():
    parser = argparse.ArgumentParser(
        description="Voice Cloning and Persian to English Translation Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Complete pipeline
  python main.py --mode complete --srt input.srt --reference-voice voice.wav --output output_dir
  
  # Just translate text
  python main.py --mode translate --text "سلام دنیا"
  
  # Just clone voice
  python main.py --mode clone --reference-voice voice.wav --text "Hello world" --output output.wav
        """
    )
    
    parser.add_argument("--mode", choices=["complete", "translate", "clone"], 
                       required=True, help="Operation mode")
    
    # Complete pipeline arguments
    parser.add_argument("--srt", help="Path to SRT subtitle file")
    parser.add_argument("--reference-voice", required=True, 
                       help="Path to reference voice file for cloning")
    parser.add_argument("--output", required=True, 
                       help="Output directory or file path")
    
    # Translation arguments
    parser.add_argument("--text", help="Persian text to translate")
    
    # Optional arguments
    parser.add_argument("--device", default="auto", 
                       help="Device to use (cuda/cpu/auto)")
    parser.add_argument("--verbose", "-v", action="store_true", 
                       help="Verbose output")
    
    args = parser.parse_args()
    
    # Determine device
    if args.device == "auto":
        device = "cuda" if torch.cuda.is_available() else "cpu"
    else:
        device = args.device
    
    print(f"Using device: {device}")
    
    try:
        # Initialize voice cloner
        cloner = VoiceCloner(device=device)
        
        if args.mode == "complete":
            if not args.srt:
                print("Error: SRT file is required for complete mode")
                sys.exit(1)
            
            print("Starting complete pipeline...")
            success = cloner.process_complete_pipeline(
                persian_audio_path=None,  # Not used in current implementation
                srt_path=args.srt,
                reference_voice_path=args.reference_voice,
                output_dir=args.output
            )
            
            if success:
                print("✅ Pipeline completed successfully!")
            else:
                print("❌ Pipeline failed!")
                sys.exit(1)
        
        elif args.mode == "translate":
            if not args.text:
                print("Error: Text is required for translate mode")
                sys.exit(1)
            
            print(f"Translating: {args.text}")
            english_text = cloner.translate_persian_to_english(args.text)
            print(f"Translation: {english_text}")
        
        elif args.mode == "clone":
            if not args.text:
                print("Error: Text is required for clone mode")
                sys.exit(1)
            
            print(f"Cloning voice for text: {args.text}")
            success = cloner.clone_voice(
                reference_audio_path=args.reference_voice,
                text=args.text,
                output_path=args.output
            )
            
            if success:
                print("✅ Voice cloning completed!")
            else:
                print("❌ Voice cloning failed!")
                sys.exit(1)
    
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    import torch
    main()