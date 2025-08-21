import os
from typing import Dict, List, Optional

import numpy as np
from pydub import AudioSegment
from TTS.api import TTS


class EnglishVoiceSynthesizer:
    """
    Synthesize English speech using Coqui XTTS v2 cloned from a Persian reference voice
    (short WAV/MP3). Produces a single AudioSegment aligned with provided segments.
    """

    def __init__(
        self,
        model_name: str = "tts_models/multilingual/multi-dataset/xtts_v2",
        device: str = "cpu",
        speaker_wav: Optional[str] = None,
        sample_rate: int = 22050,
    ) -> None:
        self.model_name = model_name
        self.device = device
        self.sample_rate = sample_rate
        self.tts = TTS(model_name).to(device)
        self.speaker_wav = speaker_wav

    def synthesize_aligned(self, segments: List[Dict[str, object]]) -> AudioSegment:
        """
        Given segments with keys: start, end, text_en produce an AudioSegment that matches timing.
        We create per-segment speech and pad/truncate to fit exactly into segment window.
        """
        if not segments:
            return AudioSegment.silent(duration=0)

        final_audio = AudioSegment.silent(duration=int(float(segments[-1]["end"]) * 1000) + 100)
        for seg in segments:
            start_ms = int(float(seg["start"]) * 1000)
            end_ms = int(float(seg["end"]) * 1000)
            dur_ms = max(0, end_ms - start_ms)
            text_en = (seg.get("text_en") or "").strip()
            if not text_en or dur_ms <= 0:
                continue

            wav = self.tts.tts(
                text=text_en,
                speaker_wav=self.speaker_wav,
                language="en",
                split_sentences=False,
            )
            # wav is numpy array float32
            seg_audio = AudioSegment(
                (np.array(wav) * (2 ** 15 - 1)).astype(np.int16).tobytes(),
                frame_rate=self.sample_rate,
                sample_width=2,
                channels=1,
            )

            # Fit to window: scale louder a bit, then pad or truncate
            if len(seg_audio) > dur_ms:
                seg_audio = seg_audio[:dur_ms]
            elif len(seg_audio) < dur_ms:
                seg_audio = seg_audio + AudioSegment.silent(duration=dur_ms - len(seg_audio))

            final_audio = final_audio.overlay(seg_audio, position=start_ms)

        return final_audio