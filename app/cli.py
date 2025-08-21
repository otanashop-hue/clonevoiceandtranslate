import argparse
import os
from pathlib import Path

from rich import print

from app.transcribe import transcribe_persian
from app.translate import translate_segments_fa_to_en, translate_segments_en_to_fa
from app.srt_utils import compose_bilingual_srt, parse_srt_to_segments
from app.tts import EnglishVoiceSynthesizer


def run_pipeline(
    input_audio: str | None,
    out_dir: str,
    speaker_ref: str | None,
    whisper_size: str,
    device: str,
    english_srt: str | None,
) -> None:
    Path(out_dir).mkdir(parents=True, exist_ok=True)

    if english_srt:
        print("[bold]Using provided English SRT...[/bold]")
        with open(english_srt, "r", encoding="utf-8") as f:
            srt_text = f.read()
        en_segments_raw = parse_srt_to_segments(srt_text)
        # normalize field name for translate function
        en_segments = [{"start": s["start"], "end": s["end"], "text_en": s["text"]} for s in en_segments_raw]
        print("[bold]Translating EN->FA for bilingual SRT...[/bold]")
        bi_segments = translate_segments_en_to_fa(en_segments)
    else:
        if not input_audio:
            raise SystemExit("When --english-srt is not provided, --input-audio is required.")
        print("[bold]Transcribing Persian audio...[/bold]")
        segments_fa = transcribe_persian(input_audio, model_size=whisper_size, device=device)
        print("[bold]Translating FA->EN...[/bold]")
        bi_segments = translate_segments_fa_to_en(segments_fa)

    print("[bold]Composing bilingual SRT...[/bold]")
    srt_out_text = compose_bilingual_srt(bi_segments)

    if input_audio:
        stem = Path(input_audio).stem
    elif english_srt:
        stem = Path(english_srt).stem
    else:
        stem = "output"

    srt_path = os.path.join(out_dir, f"{stem}.bilingual.srt")
    with open(srt_path, "w", encoding="utf-8") as f:
        f.write(srt_out_text)

    print("[bold]Synthesizing aligned English audio (voice cloned)...[/bold]")
    tts = EnglishVoiceSynthesizer(device=device, speaker_wav=speaker_ref)
    audio_seg = tts.synthesize_aligned(bi_segments)
    wav_out = os.path.join(out_dir, f"{stem}.en.cloned.wav")
    audio_seg.export(wav_out, format="wav")

    print(f"[green]Done.[/green] SRT: {srt_path} | WAV: {wav_out}")



def main() -> None:
    parser = argparse.ArgumentParser(description="FA->EN voice-clone dubbing with bilingual SRT")
    parser.add_argument("--input-audio", default=None, help="Path to input Persian audio (wav/mp3)")
    parser.add_argument("--english-srt", default=None, help="Path to an existing English SRT to use instead of transcription+translation")
    parser.add_argument("--out-dir", default="outputs", help="Output directory")
    parser.add_argument("--speaker-ref", default=None, help="Reference voice file for cloning (wav/mp3)")
    parser.add_argument("--whisper-size", default="small", help="Faster-Whisper model size: tiny, base, small, medium, large-v2")
    parser.add_argument("--device", default="cpu", help="cpu or cuda")

    args = parser.parse_args()
    run_pipeline(
        input_audio=args.input_audio,
        out_dir=args.out_dir,
        speaker_ref=args.speaker_ref,
        whisper_size=args.whisper_size,
        device=args.device,
        english_srt=args.english_srt,
    )


if __name__ == "__main__":
    main()