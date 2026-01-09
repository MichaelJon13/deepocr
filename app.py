#!/usr/bin/env python3
"""DeepSeek-OCR PDF Processor - OCR multi-page PDFs using DeepSeek-OCR via Ollama"""

import argparse
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Optional, Dict
from pdf2image import convert_from_path


# Resource limits for safety
MAX_FILE_SIZE_MB = 500  # Maximum PDF file size in MB
MAX_PAGES_DEFAULT = 500  # Default maximum pages to process in one run

# OCR prompt templates
OCR_PROMPTS: Dict[str, str] = {
    'free': 'Free OCR.',
    'layout': '<|grounding|>Given the layout of the image.',
    'markdown': '<|grounding|>Convert the document to markdown.',
    'extract': 'Extract the text in the image.',
    'figure': 'Parse the figure.',
}


def ocr_pdf(
    pdf_path: str,
    output_path: str = "output.txt",
    dpi: int = 300,
    delay: int = 0,
    start_page: int = 1,
    end_page: Optional[int] = None,
    prompt_type: str = 'free',
    model: str = 'deepseek-ocr',
    verbose: bool = False,
    max_pages: int = MAX_PAGES_DEFAULT
) -> None:
    """
    Perform OCR on a PDF file using DeepSeek-OCR via Ollama.

    Args:
        pdf_path: Path to input PDF file
        output_path: Path to output text file (default: output.txt)
        dpi: Resolution for PDF to image conversion (default: 300)
        delay: Delay in seconds between processing pages (default: 0)
        start_page: First page to process, 1-indexed (default: 1)
        end_page: Last page to process, inclusive (default: None = all pages)
        prompt_type: Type of OCR prompt to use (default: 'free')
        model: Ollama model name (default: 'deepseek-ocr')
        verbose: Enable verbose output (default: False)
        max_pages: Maximum pages to process in one run (default: 500)

    Returns:
        None

    Raises:
        SystemExit: If PDF file not found or validation fails
    """
    pdf_path = Path(pdf_path).resolve()
    output_path = Path(output_path).resolve()

    # Check if PDF exists
    if not pdf_path.exists():
        print(f"Error: File '{pdf_path}' not found", file=sys.stderr)
        sys.exit(1)

    # Check file size
    file_size_mb = pdf_path.stat().st_size / (1024 * 1024)
    if file_size_mb > MAX_FILE_SIZE_MB:
        print(f"Error: File too large ({file_size_mb:.1f}MB). Maximum allowed: {MAX_FILE_SIZE_MB}MB", file=sys.stderr)
        sys.exit(1)

    # Get OCR prompt
    ocr_prompt = OCR_PROMPTS.get(prompt_type, OCR_PROMPTS['free'])

    if verbose:
        print(f"Input: {pdf_path}")
        print(f"Output: {output_path}")
        print(f"DPI: {dpi}")
        print(f"Model: {model}")
        print(f"Prompt: {prompt_type} -> '{ocr_prompt}'")

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir = Path(temp_dir)

        # Convert PDF to images (returns PIL images)
        # Use first_page and last_page for efficient memory usage
        print(f"Converting {pdf_path.name} to images (DPI={dpi})...")
        try:
            # First, get total page count with a lightweight operation
            from pdf2image.pdf2image import pdfinfo_from_path
            try:
                info = pdfinfo_from_path(pdf_path)
                total_pages = info.get('Pages', 0)
            except:
                # Fallback: load all pages to count
                temp_images = convert_from_path(pdf_path, dpi=dpi)
                total_pages = len(temp_images)
                # Check if we can use the already loaded images
                if end_page is None or end_page >= total_pages:
                    images = temp_images[start_page - 1:]
                    print(f"Total pages in PDF: {total_pages}")
                    print(f"Processing pages {start_page} to {total_pages} ({len(images)} page(s))")
                    # Skip re-conversion below
                    total_pages = -1

            if total_pages > 0:
                print(f"Total pages in PDF: {total_pages}")

                # Validate page range
                if start_page > total_pages:
                    print(f"Error: Start page {start_page} exceeds total pages ({total_pages})", file=sys.stderr)
                    sys.exit(1)

                # Calculate actual end page
                actual_end_page = min(total_pages, end_page) if end_page else total_pages

                # Validate max pages limit
                pages_to_process = actual_end_page - start_page + 1
                if pages_to_process > max_pages:
                    print(f"Error: Too many pages to process ({pages_to_process}). Maximum allowed: {max_pages}", file=sys.stderr)
                    print(f"Tip: Use --max-pages to increase limit or adjust --start-page and --end-page", file=sys.stderr)
                    sys.exit(1)

                print(f"Processing pages {start_page} to {actual_end_page} ({pages_to_process} page(s))")

                # Only convert the pages we need (MEMORY EFFICIENT!)
                images = convert_from_path(
                    pdf_path,
                    dpi=dpi,
                    first_page=start_page,
                    last_page=actual_end_page
                )
        except Exception as e:
            print(f"Error converting PDF: {e}", file=sys.stderr)
            sys.exit(1)

        results = []
        start_time = time.time()

        # Calculate end page for display
        end_page_display = start_page + len(images) - 1

        for i, image in enumerate(images, start=start_page):
            img_path = temp_dir / f"page_{i}.png"
            image.save(img_path, 'PNG')

            page_start = time.time()
            print(f"Processing page {i}/{end_page_display}...", end=' ', flush=True)

            # Run DeepSeek-OCR via Ollama (use absolute path + \n in argument)
            result = subprocess.run(
                ["ollama", "run", model, f"{str(img_path)}\n{ocr_prompt}"],
                capture_output=True,
                text=True
            )

            page_time = time.time() - page_start

            if result.returncode != 0:
                print(f"FAILED ({page_time:.1f}s)")
                if verbose:
                    print(f"  Error: {result.stderr}", file=sys.stderr)
                results.append(f"\n=== Page {i} ===\n\n*OCR failed*\n")
            else:
                print(f"✓ ({page_time:.1f}s)")
                if verbose and result.stdout:
                    print(f"  Preview: {result.stdout[:100]}...")
                results.append(f"\n=== Page {i} ===\n\n{result.stdout}")

            # Delay between pages if specified
            if delay > 0 and i < end_page_display:
                if verbose:
                    print(f"  Waiting {delay}s...")
                time.sleep(delay)

        # Write output
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"# OCR Results: {pdf_path.name}\n")
            f.write(f"# Pages: {start_page}-{end_page_display}\n")
            f.write(f"# Prompt: {prompt_type}\n")
            f.write(f"# Model: {model}\n\n")
            f.writelines(results)

        total_time = time.time() - start_time
        print(f"\nDone! Processed {len(images)} page(s) in {total_time:.1f}s")
        print(f"Average: {total_time/len(images):.1f}s per page")
        print(f"Output saved to: {output_path}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description='OCR multi-page PDFs using DeepSeek-OCR via Ollama',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage - process entire PDF
  %(prog)s document.pdf

  # Process first 10 pages only
  %(prog)s document.pdf -o output.txt --end-page 10

  # Process pages 5-15 with layout preservation
  %(prog)s document.pdf --start-page 5 --end-page 15 --prompt layout

  # High quality with markdown output
  %(prog)s document.pdf --dpi 400 --prompt markdown -v

  # Process with delay between pages (to avoid overloading)
  %(prog)s large.pdf --delay 5 --end-page 20

Available prompts: """ + ", ".join(OCR_PROMPTS.keys())
    )

    # Required arguments
    parser.add_argument(
        'pdf',
        type=str,
        help='Input PDF file to process'
    )

    # Optional arguments
    parser.add_argument(
        '-o', '--output',
        type=str,
        default='output.txt',
        help='Output text file (default: output.txt)'
    )

    parser.add_argument(
        '--dpi',
        type=int,
        default=300,
        help='Resolution for PDF to image conversion (default: 300)'
    )

    parser.add_argument(
        '--delay',
        type=int,
        default=0,
        help='Delay in seconds between processing pages (default: 0)'
    )

    parser.add_argument(
        '--start-page',
        type=int,
        default=1,
        help='First page to process, 1-indexed (default: 1)'
    )

    parser.add_argument(
        '--end-page',
        type=int,
        default=None,
        help='Last page to process, inclusive (default: all pages)'
    )

    parser.add_argument(
        '--prompt',
        type=str,
        default='free',
        choices=list(OCR_PROMPTS.keys()),
        help='OCR prompt type (default: free)'
    )

    parser.add_argument(
        '--model',
        type=str,
        default='deepseek-ocr',
        help='Ollama model name (default: deepseek-ocr)'
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )

    parser.add_argument(
        '--max-pages',
        type=int,
        default=MAX_PAGES_DEFAULT,
        help=f'Maximum pages to process in one run (default: {MAX_PAGES_DEFAULT})'
    )

    args = parser.parse_args()

    # Validate arguments
    if args.start_page < 1:
        parser.error("--start-page must be >= 1")

    if args.end_page is not None and args.end_page < args.start_page:
        parser.error("--end-page must be >= --start-page")

    if args.dpi < 72:
        parser.error("--dpi must be >= 72")

    if args.delay < 0:
        parser.error("--delay must be >= 0")

    if args.max_pages < 1:
        parser.error("--max-pages must be >= 1")

    # Run OCR
    ocr_pdf(
        pdf_path=args.pdf,
        output_path=args.output,
        dpi=args.dpi,
        delay=args.delay,
        start_page=args.start_page,
        end_page=args.end_page,
        prompt_type=args.prompt,
        model=args.model,
        verbose=args.verbose,
        max_pages=args.max_pages
    )


if __name__ == "__main__":
    main()
