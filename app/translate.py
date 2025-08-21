import time
from typing import Dict, List

from deep_translator import GoogleTranslator


def translate_segments_fa_to_en(segments: List[Dict[str, object]], max_retries: int = 3, sleep_seconds: float = 0.7) -> List[Dict[str, object]]:
    """
    Translate each segment's Persian text (key: "text") to English and return augmented dicts:
      { start: float, end: float, text_fa: str, text_en: str }
    """
    translator = GoogleTranslator(source="fa", target="en")
    translated: List[Dict[str, object]] = []

    for seg in segments:
        source_text = (seg.get("text") or "").strip()
        text_en = ""

        for attempt in range(max_retries):
            try:
                if source_text:
                    text_en = translator.translate(source_text)
                break
            except Exception:
                if attempt == max_retries - 1:
                    text_en = source_text
                else:
                    time.sleep(sleep_seconds)

        translated.append({
            "start": float(seg.get("start", 0.0)),
            "end": float(seg.get("end", 0.0)),
            "text_fa": source_text,
            "text_en": (text_en or source_text).strip(),
        })

    return translated


def translate_segments_en_to_fa(segments: List[Dict[str, object]], max_retries: int = 3, sleep_seconds: float = 0.7) -> List[Dict[str, object]]:
    """
    Translate each segment's English text (key: "text_en" or "text") to Persian and return augmented dicts:
      { start: float, end: float, text_en: str, text_fa: str }
    """
    translator = GoogleTranslator(source="en", target="fa")
    translated: List[Dict[str, object]] = []

    for seg in segments:
        src_text = (seg.get("text_en") or seg.get("text") or "").strip()
        text_fa = ""

        for attempt in range(max_retries):
            try:
                if src_text:
                    text_fa = translator.translate(src_text)
                break
            except Exception:
                if attempt == max_retries - 1:
                    text_fa = src_text
                else:
                    time.sleep(sleep_seconds)

        translated.append({
            "start": float(seg.get("start", 0.0)),
            "end": float(seg.get("end", 0.0)),
            "text_en": src_text,
            "text_fa": (text_fa or src_text).strip(),
        })

    return translated