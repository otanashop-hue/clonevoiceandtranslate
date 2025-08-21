from datetime import timedelta
from typing import Dict, List

import srt


def compose_bilingual_srt(segments: List[Dict[str, object]]) -> str:
    """
    Build an SRT string where each caption contains the English line on the first line
    and the Persian line on the second line.

    Expects segment dicts with: start: float, end: float, text_en: str, text_fa: str
    """
    subtitles: List[srt.Subtitle] = []

    for idx, seg in enumerate(segments, start=1):
        start_td = timedelta(seconds=float(seg.get("start", 0.0)))
        end_td = timedelta(seconds=float(seg.get("end", 0.0)))
        text_en = (seg.get("text_en") or "").strip()
        text_fa = (seg.get("text_fa") or "").strip()
        content = f"{text_en}\n{text_fa}".strip()
        subtitles.append(srt.Subtitle(index=idx, start=start_td, end=end_td, content=content))

    return srt.compose(subtitles)


def parse_srt_to_segments(srt_text: str) -> List[Dict[str, object]]:
    """
    Parse SRT text into a list of segments with keys: start, end, text
    """
    subs = list(srt.parse(srt_text))
    segments: List[Dict[str, object]] = []
    for sub in subs:
        segments.append({
            "start": sub.start.total_seconds(),
            "end": sub.end.total_seconds(),
            "text": sub.content.strip(),
        })
    return segments