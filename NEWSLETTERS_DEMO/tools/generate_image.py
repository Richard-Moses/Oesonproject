"""
Generate an image from a text prompt using Gemini 2.5 Flash Image
("Nano Banana").

CLI usage:
    python tools/generate_image.py "<prompt>" <output_path.png>

Requires GEMINI_API_KEY in .env (free tier: https://aistudio.google.com/apikey).
Used for both the newsletter logo (generate once, reuse) and the per-issue
infographic (regenerate each run).
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from google import genai

load_dotenv()

MODEL = "gemini-2.5-flash-image"


class ImageGenerationError(RuntimeError):
    pass


def generate_image(prompt: str, output_path: Path) -> Path:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ImageGenerationError(
            "No GEMINI_API_KEY found in .env. Get a free key at "
            "https://aistudio.google.com/apikey and add it to .env."
        )

    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(model=MODEL, contents=[prompt])

    for part in response.candidates[0].content.parts:
        if part.inline_data is not None:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_bytes(part.inline_data.data)
            return output_path

    raise ImageGenerationError(f"No image returned for prompt: {prompt!r}")


def main():
    if len(sys.argv) != 3:
        print('Usage: python tools/generate_image.py "<prompt>" <output_path.png>', file=sys.stderr)
        sys.exit(1)

    prompt, output_path = sys.argv[1], Path(sys.argv[2])
    try:
        result = generate_image(prompt, output_path)
    except ImageGenerationError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    print(f"Image saved to {result}")


if __name__ == "__main__":
    main()
