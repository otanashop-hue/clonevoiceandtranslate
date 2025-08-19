"""
SRT File Utilities
ابزارهای پردازش فایل SRT
"""

import pysrt
import os
import re
from typing import List, Dict, Tuple

class SRTProcessor:
    def __init__(self):
        pass
    
    def validate_srt_file(self, srt_path: str) -> bool:
        """
        Validate SRT file format and content
        
        Args:
            srt_path: Path to SRT file
            
        Returns:
            True if valid, False otherwise
        """
        try:
            subs = pysrt.open(srt_path)
            if len(subs) == 0:
                print("Warning: SRT file is empty")
                return False
            
            # Check for basic format issues
            for i, sub in enumerate(subs):
                if not sub.text.strip():
                    print(f"Warning: Empty subtitle at index {i}")
                
                if sub.start >= sub.end:
                    print(f"Error: Invalid timing at index {i} (start >= end)")
                    return False
            
            print(f"✅ SRT file is valid with {len(subs)} subtitles")
            return True
            
        except Exception as e:
            print(f"❌ SRT file validation failed: {e}")
            return False
    
    def extract_persian_text(self, srt_path: str) -> List[str]:
        """
        Extract Persian text from SRT file
        
        Args:
            srt_path: Path to SRT file
            
        Returns:
            List of Persian text segments
        """
        try:
            subs = pysrt.open(srt_path)
            texts = [sub.text.strip() for sub in subs if sub.text.strip()]
            return texts
        except Exception as e:
            print(f"Error extracting text: {e}")
            return []
    
    def create_sample_srt(self, output_path: str = "sample.srt"):
        """
        Create a sample SRT file for testing
        
        Args:
            output_path: Path to save the sample SRT file
        """
        sample_content = """1
00:00:01,000 --> 00:00:04,000
سلام، این یک نمونه متن فارسی است

2
00:00:04,500 --> 00:00:08,000
امیدوارم که این پروژه برای شما مفید باشد

3
00:00:08,500 --> 00:00:12,000
این سیستم می‌تواند صدا را کلون کند و متن را ترجمه کند

4
00:00:12,500 --> 00:00:16,000
و در نهایت یک فایل صوتی همزمان شده تولید کند

5
00:00:16,500 --> 00:00:20,000
با تشکر از استفاده از این ابزار"""
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(sample_content)
        
        print(f"Sample SRT file created: {output_path}")
    
    def analyze_srt_timing(self, srt_path: str) -> Dict:
        """
        Analyze timing information in SRT file
        
        Args:
            srt_path: Path to SRT file
            
        Returns:
            Dictionary with timing analysis
        """
        try:
            subs = pysrt.open(srt_path)
            
            total_duration = subs[-1].end.ordinal
            avg_duration = sum(sub.end.ordinal - sub.start.ordinal for sub in subs) / len(subs)
            
            gaps = []
            for i in range(len(subs) - 1):
                gap = subs[i+1].start.ordinal - subs[i].end.ordinal
                gaps.append(gap)
            
            analysis = {
                'total_subtitles': len(subs),
                'total_duration_ms': total_duration,
                'total_duration_seconds': total_duration / 1000,
                'average_segment_duration_ms': avg_duration,
                'average_gap_ms': sum(gaps) / len(gaps) if gaps else 0,
                'min_gap_ms': min(gaps) if gaps else 0,
                'max_gap_ms': max(gaps) if gaps else 0
            }
            
            return analysis
            
        except Exception as e:
            print(f"Error analyzing SRT timing: {e}")
            return {}
    
    def print_srt_analysis(self, srt_path: str):
        """
        Print detailed analysis of SRT file
        
        Args:
            srt_path: Path to SRT file
        """
        print(f"Analyzing SRT file: {srt_path}")
        print("=" * 50)
        
        # Validate file
        if not self.validate_srt_file(srt_path):
            return
        
        # Get timing analysis
        analysis = self.analyze_srt_timing(srt_path)
        
        if analysis:
            print(f"Total subtitles: {analysis['total_subtitles']}")
            print(f"Total duration: {analysis['total_duration_seconds']:.2f} seconds")
            print(f"Average segment duration: {analysis['average_segment_duration_ms']:.1f} ms")
            print(f"Average gap between segments: {analysis['average_gap_ms']:.1f} ms")
            print(f"Min gap: {analysis['min_gap_ms']:.1f} ms")
            print(f"Max gap: {analysis['max_gap_ms']:.1f} ms")
        
        # Show first few subtitles
        print("\nFirst 3 subtitles:")
        print("-" * 30)
        try:
            subs = pysrt.open(srt_path)
            for i, sub in enumerate(subs[:3]):
                print(f"{i+1}. {sub.start} --> {sub.end}")
                print(f"   {sub.text}")
                print()
        except Exception as e:
            print(f"Error reading subtitles: {e}")

def main():
    """
    Example usage of SRT utilities
    """
    processor = SRTProcessor()
    
    # Create sample SRT file
    processor.create_sample_srt()
    
    # Analyze the sample file
    processor.print_srt_analysis("sample.srt")

if __name__ == "__main__":
    main()