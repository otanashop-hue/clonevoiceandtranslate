from typing import Dict, Iterable, List, Tuple

from faster_whisper import WhisperModel


def _pick_compute_type(device: str) -> str:
    device_norm = (device or "cpu").lower()
    if device_norm in {"cuda", "gpu"}:
        return "float16"
    return "int8"


def transcribe_persian(
    audio_path: str,
    model_size: str = "small",
    device: str = "cpu",
    beam_size: int = 5,
    vad_filter: bool = True,
) -> List[Dict[str, object]]:
    """
    Transcribe a Persian audio file to segments using Faster-Whisper.

    Returns list of dicts: { start: float, end: float, text: str }
    """
    compute_type = _pick_compute_type(device)
    model = WhisperModel(model_size, device=device, compute_type=compute_type)

    segments, _info = model.transcribe(
        audio_path,
        language="fa",
        beam_size=beam_size,
        vad_filter=vad_filter,
        vad_parameters=dict(min_silence_duration_ms=500),
    )

    results: List[Dict[str, object]] = []
    for seg in segments:  # type: ignore[assignment]
        results.append({
            "start": float(seg.start),
            "end": float(seg.end),
            "text": (seg.text or "").strip(),
        })
    return results