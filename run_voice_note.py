import argparse
import base64
from pathlib import Path

from property_audio.audio_intake import transcribe_and_dispatch
from property_audio.models import AudioFormat, PropertyAudioRequest


def main() -> None:
    parser = argparse.ArgumentParser(description="Process one property voice note")
    parser.add_argument("audio", type=Path)
    parser.add_argument("--property-id", required=True)
    args = parser.parse_args()

    audio_format = AudioFormat(args.audio.suffix.lstrip(".").lower())
    request = PropertyAudioRequest(
        property_id=args.property_id,
        audio_base64=base64.b64encode(args.audio.read_bytes()).decode("ascii"),
        audio_format=audio_format,
    )
    print(transcribe_and_dispatch(request).model_dump_json(indent=2))


if __name__ == "__main__":
    main()

