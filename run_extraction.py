import argparse
import time
from pathlib import Path

from app.extract import PROVIDER, extract_action_items

TRANSCRIPTS_DIR = Path("data/transcripts")
OUTPUTS_DIR = Path("data/outputs")

# Groq's free tier caps tokens per minute; a short pause between transcripts
# keeps a run of short transcripts comfortably under an 8K TPM budget.
GROQ_PAUSE_SECONDS = 15


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true", help="Re-run and overwrite existing outputs")
    args = parser.parse_args()

    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

    transcript_paths = sorted(TRANSCRIPTS_DIR.glob("*.txt"))
    for i, path in enumerate(transcript_paths):
        output_path = OUTPUTS_DIR / f"{path.stem}_{PROVIDER}.json"
        print(f"--- {path.name} ---")

        if output_path.exists() and not args.force:
            print(f"Skipped {path.name}: {output_path} already exists")
            print()
            continue

        transcript = path.read_text()
        try:
            result = extract_action_items(transcript)
        except Exception as e:
            print(f"Failed to process {path.name}: {e}")
            print()
            continue

        output_path.write_text(result.model_dump_json(indent=2))
        print(result.model_dump_json(indent=2))
        print()

        if PROVIDER == "groq" and i < len(transcript_paths) - 1:
            time.sleep(GROQ_PAUSE_SECONDS)


if __name__ == "__main__":
    main()
