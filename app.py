#!/usr/bin/env python3
# ocr_pdf.py - OCR multi-page PDF using DeepSeek-OCR

import subprocess
import sys
import tempfile
import time
from pathlib import Path
from pdf2image import convert_from_path

def ocr_pdf(pdf_path, output_path="output.txt", dpi=300, delay=0):
    pdf_path = Path(pdf_path).resolve()
    output_path = Path(output_path).resolve()

    # Check if PDF exists
    if not pdf_path.exists():
        print(f"Error: File '{pdf_path}' not found", file=sys.stderr)
        sys.exit(1)

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir = Path(temp_dir)

        # Convert PDF to images (returns PIL images)
        print(f"Converting {pdf_path.name} to images...")
        try:
            images = convert_from_path(pdf_path, dpi=dpi)
        except Exception as e:
            print(f"Error converting PDF: {e}", file=sys.stderr)
            sys.exit(1)

        results = []
        for i, image in enumerate(images, 1):
            img_path = temp_dir / f"page_{i}.png"
            image.save(img_path, 'PNG')

            print(f"Processing page {i}/{len(images)}...")

            # Run DeepSeek-OCR via Ollama (use absolute path + \n in argument)
            result = subprocess.run(
                ["ollama", "run", "deepseek-ocr", f"{str(img_path)}\nFree OCR."],
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                print(f"Warning: OCR failed for page {i}: {result.stderr}", file=sys.stderr)
                results.append(f"\n=== Page {i} ===\n\n*OCR failed*\n")
            else:
                results.append(f"\n=== Page {i} ===\n\n{result.stdout}")

            # Delay between pages if specified
            if delay > 0 and i < len(images):
                time.sleep(delay)

        # Write output
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"# OCR Results: {pdf_path.name}\n")
            f.writelines(results)

        print(f"Done! Output saved to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python ocr_pdf.py <input.pdf> [output.txt] [dpi] [delay_seconds]")
        sys.exit(1)

    pdf = sys.argv[1]
    output = sys.argv[2] if len(sys.argv) > 2 else "output.txt"

    try:
        dpi = int(sys.argv[3]) if len(sys.argv) > 3 else 300
    except ValueError:
        print(f"Error: DPI must be an integer, got '{sys.argv[3]}'", file=sys.stderr)
        sys.exit(1)

    try:
        delay = int(sys.argv[4]) if len(sys.argv) > 4 else 0
    except ValueError:
        print(f"Error: Delay must be an integer, got '{sys.argv[4]}'", file=sys.stderr)
        sys.exit(1)

    ocr_pdf(pdf, output, dpi, delay)
