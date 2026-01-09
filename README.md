# DeepSeek-OCR Ollama CLI Cheat Sheet

*Last updated: January 2026 | Ollama v0.13.0+ required*

## Table of Contents

- [Installation & Setup](#installation--setup)
- [Quick Start](#quick-start)
- [app.py - Python CLI Tool](#apppy---python-cli-tool)
- [Model Info](#model-info)
- [Important Notes](#%EF%B8%8F-important-notes)
- [20 Example CLI Prompts](#20-example-cli-prompts)
- [Prompt Reference](#prompt-reference)
- [Batch Processing Script](#batch-processing-script)
- [Multi-Page PDF OCR](#multi-page-pdf-ocr)
- [API Usage (curl)](#api-usage-curl)
- [Useful Ollama Commands](#useful-ollama-commands)
- [Resolution Modes](#resolution-modes-from-github)
- [Troubleshooting](#troubleshooting)
- [Resources](#resources)

---

## Installation & Setup

### 1. Install Ollama

**Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**macOS:**
```bash
# Download and install from ollama.com
# Or use Homebrew
brew install ollama

# Start Ollama service
ollama serve
```

**Windows:**
```bash
# Download installer from https://ollama.com/download/windows
# Run the installer and follow the prompts
```

### 2. Verify Installation

```bash
# Check Ollama version (requires v0.13.0+)
ollama --version

# Start Ollama service (if not already running)
ollama serve
```

### 3. Pull the DeepSeek-OCR Model

```bash
# Download the model (6.7GB download)
ollama pull deepseek-ocr

# Verify the model is installed
ollama list

# Check model details
ollama show deepseek-ocr
```

### 4. Install Python Dependencies (for app.py)

```bash
# Install required packages
pip install pdf2image Pillow

# Install poppler (required by pdf2image)
# Ubuntu/Debian:
sudo apt install poppler-utils

# macOS:
brew install poppler

# Windows:
# Download from https://github.com/oschwartz10612/poppler-windows/releases
# Add bin folder to PATH
```

---

## Quick Start

```bash
# Install/Pull the model (requires Ollama v0.13.0+)
ollama pull deepseek-ocr

# Check model info
ollama show deepseek-ocr

# Run benchmark stats
ollama ps
```

### Quick Test

```bash
# Basic OCR test (replace with your image)
ollama run deepseek-ocr "./test.png\nFree OCR."

# With layout preservation
ollama run deepseek-ocr "./document.png\n<|grounding|>Convert the document to markdown."
```

---

## app.py - Python CLI Tool

This repository includes `app.py`, a powerful command-line tool for OCR processing of multi-page PDFs using DeepSeek-OCR.

### Features

- **Multiple OCR prompt types** - Choose from `free`, `layout`, `markdown`, `extract`, or `figure`
- **Page range selection** - Process specific page ranges (e.g., pages 5-15)
- **Flexible output** - Control DPI, delay between pages, and output format
- **Progress tracking** - Real-time progress with timing statistics
- **Verbose mode** - Detailed output for debugging

### Quick Usage

```bash
# View help and all options
python app.py --help

# Basic usage - process entire PDF
python app.py document.pdf

# Process first 10 pages only
python app.py 179pageExample.pdf --end-page 10

# Process pages 5-15 with layout preservation
python app.py document.pdf --start-page 5 --end-page 15 --prompt layout

# High quality markdown output with verbose mode
python app.py document.pdf -o output.md --dpi 400 --prompt markdown -v

# Process with delay to avoid overloading (5 sec between pages)
python app.py large.pdf --delay 5 --end-page 20 -v
```

### Command-Line Options

```
usage: app.py [-h] [-o OUTPUT] [--dpi DPI] [--delay DELAY]
              [--start-page START_PAGE] [--end-page END_PAGE]
              [--prompt {free,layout,markdown,extract,figure}]
              [--model MODEL] [-v]
              pdf

positional arguments:
  pdf                   Input PDF file to process

optional arguments:
  -h, --help            Show help message and exit
  -o, --output OUTPUT   Output text file (default: output.txt)
  --dpi DPI             Resolution for PDF to image conversion (default: 300)
  --delay DELAY         Delay in seconds between processing pages (default: 0)
  --start-page START    First page to process, 1-indexed (default: 1)
  --end-page END        Last page to process, inclusive (default: all pages)
  --prompt TYPE         OCR prompt type (default: free)
  --model MODEL         Ollama model name (default: deepseek-ocr)
  -v, --verbose         Enable verbose output
```

### OCR Prompt Types

| Prompt Type | Description | Use Case |
|-------------|-------------|----------|
| `free` | Simple text extraction | Basic OCR, plain text |
| `layout` | Layout-aware parsing | Multi-column documents, complex layouts |
| `markdown` | Convert to Markdown | Structured documents, reports |
| `extract` | Extract text | General text extraction |
| `figure` | Parse figures/charts | Diagrams, charts, scientific figures |

### Examples

**1. Test with included PDF (first 10 pages)**
```bash
python app.py 179pageExample.pdf --end-page 10 -o test_output.txt
```

**2. High-quality document conversion to Markdown**
```bash
python app.py report.pdf --dpi 400 --prompt markdown -o report.md
```

**3. Process specific page range with layout preservation**
```bash
python app.py book.pdf --start-page 20 --end-page 50 --prompt layout -v
```

**4. Large PDF with delay to prevent overload**
```bash
python app.py large_scan.pdf --delay 10 --end-page 100 -v
```

**5. Scientific paper with figure parsing**
```bash
python app.py paper.pdf --prompt figure --dpi 400 -o paper_ocr.txt
```

### Sample Output

```
Converting 179pageExample.pdf to images (DPI=300)...
Total pages in PDF: 179
Processing pages 1 to 10 (10 page(s))
Processing page 1/10... ✓ (12.3s)
Processing page 2/10... ✓ (11.8s)
Processing page 3/10... ✓ (12.1s)
...
Done! Processed 10 page(s) in 121.5s
Average: 12.2s per page
Output saved to: output.txt
```

---

## Model Info

| Property | Value |
|----------|-------|
| Model Size | 6.7GB |
| Context Window | 8K |
| Input Types | Text, Image |
| Parameters | 3B |

### Supported Image Formats

| Format | Supported |
|--------|-----------|
| PNG | ✅ |
| JPG/JPEG | ✅ |
| GIF | ✅ |
| WebP | ✅ |
| PDF | ❌ (convert to images first) |

---

## ⚠️ Important Notes

- **Prompt sensitivity**: The model is sensitive to punctuation and newlines. Missing `\n` or periods can cause improper output.
- **Always use `\n`** between the image path and the prompt text.
- **Use `<|grounding|>`** for layout-aware document conversion.

---

## 20 Example CLI Prompts

> **Note:** These examples show the prompt format. Ollama interprets `\n` directly in the argument string as a newline - just include it literally like `"./image.png\nFree OCR."`. Use full absolute paths for reliability in scripts.

### Basic OCR Operations

**1. Simple Free OCR (no layout)**
```bash
ollama run deepseek-ocr "./document.png\nFree OCR."
```

**2. Extract text from image**
```bash
ollama run deepseek-ocr "./screenshot.jpg\nExtract the text in the image."
```

**3. Layout-aware document parsing**
```bash
ollama run deepseek-ocr "./document.png\n<|grounding|>Given the layout of the image."
```

**4. Convert document to Markdown**
```bash
ollama run deepseek-ocr "./report.png\n<|grounding|>Convert the document to markdown."
```

**5. Parse a figure or chart**
```bash
ollama run deepseek-ocr "./chart.png\nParse the figure."
```

---

### Document Types

**6. Invoice processing**
```bash
ollama run deepseek-ocr "./invoice.jpg\n<|grounding|>Convert the document to markdown."
```

**7. Receipt OCR**
```bash
ollama run deepseek-ocr "./receipt.png\nFree OCR."
```

**8. Business card extraction**
```bash
ollama run deepseek-ocr "./businesscard.jpg\nExtract the text in the image."
```

**9. Handwritten notes**
```bash
ollama run deepseek-ocr "./handwritten.png\nFree OCR."
```

**10. Table extraction**
```bash
ollama run deepseek-ocr "./table.png\n<|grounding|>Convert the document to markdown."
```

---

### Specialized Tasks

**11. Multi-column document**
```bash
ollama run deepseek-ocr "./newspaper.png\n<|grounding|>Given the layout of the image."
```

**12. Code screenshot**
```bash
ollama run deepseek-ocr "./code_screenshot.png\nExtract the text in the image."
```

**13. Scanned book page**
```bash
ollama run deepseek-ocr "./book_page.jpg\n<|grounding|>Convert the document to markdown."
```

**14. Whiteboard photo**
```bash
ollama run deepseek-ocr "./whiteboard.jpg\nFree OCR."
```

**15. Scientific paper/formula**
```bash
ollama run deepseek-ocr "./paper.png\n<|grounding|>Convert the document to markdown."
```

---

### Image Description & Analysis

**16. General image description**
```bash
ollama run deepseek-ocr "./photo.jpg\nDescribe this image in detail."
```

**17. Diagram interpretation**
```bash
ollama run deepseek-ocr "./diagram.png\nParse the figure."
```

**18. Form field extraction**
```bash
ollama run deepseek-ocr "./form.png\n<|grounding|>Given the layout of the image."
```

**19. Menu/price list**
```bash
ollama run deepseek-ocr "./menu.jpg\n<|grounding|>Convert the document to markdown."
```

**20. ID/License scan**
```bash
ollama run deepseek-ocr "./license.png\nExtract the text in the image."
```

---

## Prompt Reference

| Use Case | Prompt Template |
|----------|-----------------|
| Simple text extraction | `"<path>\nFree OCR."` |
| With layout preservation | `"<path>\n<\|grounding\|>Given the layout of the image."` |
| Convert to Markdown | `"<path>\n<\|grounding\|>Convert the document to markdown."` |
| Extract text | `"<path>\nExtract the text in the image."` |
| Parse figures/charts | `"<path>\nParse the figure."` |
| Describe image | `"<path>\nDescribe this image in detail."` |

> **Note:** The pipe characters in `<|grounding|>` are escaped with backslashes in the table for markdown rendering. In actual commands, type `<|grounding|>` directly without backslashes.

---

## Batch Processing Script

```bash
#!/bin/bash
# batch_ocr.sh - Process multiple images

shopt -s nullglob  # Handle no matches gracefully

# Use absolute paths
INPUT_DIR="$(realpath ./images)"
OUTPUT_DIR="$(realpath ./ocr_results)"
mkdir -p "$OUTPUT_DIR"

count=0
for img in "$INPUT_DIR"/*.png "$INPUT_DIR"/*.jpg "$INPUT_DIR"/*.jpeg; do
    if [ -f "$img" ]; then
        filename=$(basename "$img")
        echo "Processing: $filename"
        ollama run deepseek-ocr "$img\nFree OCR." > "$OUTPUT_DIR/${filename%.*}.txt"
        ((count++))
    fi
done

echo "Done! Processed $count files. Results in $OUTPUT_DIR"
```

> **Note:** This script processes image files only. Uses full paths for reliability. For PDFs, see the Multi-Page PDF OCR section below.

---

## Multi-Page PDF OCR

DeepSeek-OCR processes single images, not multi-page PDFs directly. Convert PDF pages to images first.

### Quick One-Liner

```bash
# Output to terminal (stdout)
pdftoppm -png -r 300 doc.pdf pg 2>/dev/null && for f in pg-*.png; do ollama run deepseek-ocr "$f\nFree OCR."; done

# Save to file (use full paths for reliability)
pdftoppm -png -r 300 /path/to/doc.pdf /path/to/pg 2>/dev/null && for f in /path/to/pg-*.png; do echo "Processing: $f" >&2; ollama run deepseek-ocr "$f\nFree OCR." >> /path/to/output.txt; done

# With delay between pages (10 sec) and cleanup
pdftoppm -png -r 300 /path/to/doc.pdf /path/to/pg 2>/dev/null && for f in /path/to/pg-*.png; do echo "Processing: $f" >&2; ollama run deepseek-ocr "$f\nFree OCR." >> /path/to/output.txt; sleep 10; done && rm /path/to/pg-*.png
```

> **Important:** Use full absolute paths for both the PNG prefix and output file to avoid issues. Ollama interprets `\n` in the argument string directly - do NOT pipe the prompt with `echo`.

### Step-by-Step

```bash
# 1. Convert PDF to images (one per page) - use full path for output prefix
pdftoppm -png -r 300 /path/to/scanned_document.pdf /path/to/page 2>/dev/null

# This creates: /path/to/page-001.png, /path/to/page-002.png, etc.

# 2. OCR each page (use full paths, append to file with >>)
for img in /path/to/page-*.png; do
    echo "Processing: $img" >&2
    ollama run deepseek-ocr "$img\nFree OCR." >> /path/to/output.txt
    sleep 10  # Optional delay between pages
done

# 3. Cleanup temp images (optional)
rm /path/to/page-*.png
```

> **Note:** Use `>>` to append to file. The `\n` goes directly in the argument string - Ollama interprets it as a newline. Use `2>/dev/null` after pdftoppm to suppress ICC profile warnings.

### Full PDF OCR Script

```bash
#!/bin/bash
# ocr_pdf.sh <input.pdf> [output.txt] [delay_seconds]

set -e  # Exit on error

PDF="$1"
OUTPUT="${2:-output.txt}"
DELAY="${3:-0}"

# Check arguments
if [ -z "$PDF" ]; then
    echo "Usage: ocr_pdf.sh <input.pdf> [output.txt] [delay_seconds]"
    exit 1
fi

# Check if PDF exists
if [ ! -f "$PDF" ]; then
    echo "Error: File '$PDF' not found"
    exit 1
fi

# Use absolute paths
PDF=$(realpath "$PDF")
OUTPUT=$(realpath -m "$OUTPUT")
TEMP_DIR=$(mktemp -d)

# Cleanup on exit or interrupt
trap "rm -rf \"$TEMP_DIR\"" EXIT

# Convert PDF to images
echo "Converting PDF to images..."
pdftoppm -png -r 300 "$PDF" "$TEMP_DIR/page" 2>/dev/null

# Process each page
> "$OUTPUT"
page_count=0
for img in "$TEMP_DIR"/page-*.png; do
    PAGE=$(basename "$img" .png)
    echo "Processing $PAGE..."
    echo -e "\n=== $PAGE ===\n" >> "$OUTPUT"
    ollama run deepseek-ocr "$img\nFree OCR." >> "$OUTPUT"
    ((page_count++))
    [ "$DELAY" -gt 0 ] && sleep "$DELAY"
done

echo "Done! Processed $page_count pages. Output: $OUTPUT"
```

**Usage:**
```bash
chmod +x ocr_pdf.sh
./ocr_pdf.sh my_scanned_doc.pdf results.txt       # No delay
./ocr_pdf.sh my_scanned_doc.pdf results.txt 10    # 10 sec delay between pages
```

### Alternative: ImageMagick

```bash
# ImageMagick 7+ (Linux/macOS/Windows)
magick -density 300 document.pdf page-%d.png

# ImageMagick 6 (legacy Linux)
convert -density 300 document.pdf page-%d.png
```

**Installation:**
```bash
# Ubuntu/Debian
sudo apt install imagemagick

# macOS
brew install imagemagick

# Windows: Download from https://imagemagick.org/script/download.php
```

### Requirements

#### System Packages

| Tool | Install Command | Purpose |
|------|-----------------|---------|
| pdftoppm | `sudo apt install poppler-utils` | PDF to image conversion |
| ImageMagick | `sudo apt install imagemagick` | Alternative converter |

**macOS:**
```bash
brew install poppler
```

**Windows:**
```bash
# Download from: https://github.com/oschwartz10612/poppler-windows/releases
# Add bin folder to PATH
```

#### Python Alternative (pdf2image)

```bash
# Install the Python package
pip install pdf2image

# Still requires poppler backend:
# Ubuntu/Debian: sudo apt install poppler-utils
# macOS: brew install poppler
# Windows: download poppler and add to PATH
```

**Python script for multi-page PDF OCR:**

```python
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
```

**Usage:**
```bash
pip install pdf2image Pillow
python ocr_pdf.py document.pdf output.txt 300      # No delay
python ocr_pdf.py document.pdf output.txt 300 10   # 10 sec delay between pages
```

> **Tip:** Use `dpi=300` for good quality. Increase to `dpi=400` for documents with small text.

---

## API Usage (curl)

```bash
# Single image OCR via API
# macOS:
curl -X POST http://localhost:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "model": "deepseek-ocr",
    "prompt": "<|grounding|>Convert the document to markdown.",
    "images": ["'$(base64 -i document.png)'"],
    "stream": false
  }'

# Linux:
curl -X POST http://localhost:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "model": "deepseek-ocr",
    "prompt": "<|grounding|>Convert the document to markdown.",
    "images": ["'$(base64 -w 0 document.png)'"],
    "stream": false
  }'
```

---

## Useful Ollama Commands

```bash
# Check Ollama version
ollama --version

# List all models
ollama list

# Show model details
ollama show deepseek-ocr

# Check running models & stats
ollama ps

# Run with verbose output (shows tokens/sec)
ollama run --verbose deepseek-ocr "./image.png"$'\n'"Free OCR."

# Remove model
ollama rm deepseek-ocr

# Copy/create alias
ollama cp deepseek-ocr my-ocr
```

---

## Resolution Modes (from GitHub)

| Mode | Resolution | Vision Tokens |
|------|------------|---------------|
| Tiny | 512×512 | 64 |
| Small | 640×640 | 100 |
| Base | 1024×1024 | 256 |
| Large | 1280×1280 | 400 |
| Gundam (Dynamic) | n×640×640 + 1×1024×1024 | Variable |

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| No output / garbled text | Check `\n` between path and prompt |
| Empty output file | Use full absolute paths for images and output file |
| Missing layout | Add `<\|grounding\|>` token to prompt |
| Model not found | Run `ollama pull deepseek-ocr` |
| Slow performance | Check GPU with `ollama ps` |
| Version error | Upgrade to Ollama v0.13.0+ |
| PDF not working | Convert to images first (see Multi-Page PDF section) |
| ICC profile warnings | Add `2>/dev/null` after pdftoppm command |
| Loop not working | Use full paths in glob: `/full/path/pg-*.png` |

> **Note:** The `<|grounding|>` token is shown escaped in the table. Use `<|grounding|>` (without backslashes) in commands. Always use absolute paths in scripts for reliability.

---

## Resources

- **Ollama Model Page**: https://ollama.com/library/deepseek-ocr
- **GitHub Repo**: https://github.com/deepseek-ai/DeepSeek-OCR
- **Arxiv Paper**: https://arxiv.org/abs/2510.18234
- **HuggingFace**: https://huggingface.co/deepseek-ai/DeepSeek-OCR
