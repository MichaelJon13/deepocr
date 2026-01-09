# AI Agent Development Best Practices

*A comprehensive guide for developing robust and effective AI agents*

## Table of Contents

- [Core Principles](#core-principles)
- [Prompt Engineering](#prompt-engineering)
- [Tool Design & Integration](#tool-design--integration)
- [Error Handling & Resilience](#error-handling--resilience)
- [Performance Optimization](#performance-optimization)
- [Testing & Validation](#testing--validation)
- [Documentation](#documentation)
- [Security Considerations](#security-considerations)
- [Common Pitfalls](#common-pitfalls)
- [Specific Patterns](#specific-patterns)

---

## Core Principles

### 1. Single Responsibility
Each agent or tool should have a clear, well-defined purpose.

**Good:**
```python
def ocr_pdf(pdf_path, output_path, dpi=300):
    """Convert PDF to text using OCR."""
    # Focused on PDF OCR only
```

**Bad:**
```python
def process_document(doc_path, do_ocr=True, translate=False, summarize=False):
    """Do many different things..."""
    # Too many responsibilities
```

### 2. Explicit Over Implicit
Make behavior clear and predictable. Avoid magic defaults that surprise users.

**Good:**
```python
parser.add_argument('--dpi', type=int, default=300,
                   help='Resolution for PDF conversion (default: 300)')
```

**Bad:**
```python
# DPI automatically adjusted based on file size
dpi = calculate_optimal_dpi(pdf_path)  # User has no control
```

### 3. Fail Fast & Clearly
Detect and report errors early with actionable messages.

**Good:**
```python
if not pdf_path.exists():
    print(f"Error: File '{pdf_path}' not found", file=sys.stderr)
    sys.exit(1)
```

**Bad:**
```python
try:
    # Fails deep in processing with cryptic error
    process(pdf_path)
except:
    print("Error occurred")
```

---

## Prompt Engineering

### 1. Structure & Clarity

**Template Format:**
```python
# Define clear, reusable prompts
OCR_PROMPTS = {
    'free': 'Free OCR.',
    'layout': '<|grounding|>Given the layout of the image.',
    'markdown': '<|grounding|>Convert the document to markdown.',
}
```

**Benefits:**
- Easy to test different prompts
- Consistent formatting
- Simple to extend

### 2. Context Window Management

**Problem:** Large documents exceed context limits

**Solution:**
```python
# Process in chunks
for page in pages:
    result = process_page(page)  # Independent processing
    results.append(result)
```

### 3. Prompt Versioning

Track prompt changes to understand performance variations:

```python
PROMPT_VERSION = "2.0"  # Track changes over time

OCR_PROMPTS = {
    'markdown': {
        'v1': 'Convert to markdown.',
        'v2': '<|grounding|>Convert the document to markdown.',  # Current
    }
}
```

---

## Tool Design & Integration

### 1. CLI Best Practices

**Use argparse for robust argument parsing:**

```python
parser = argparse.ArgumentParser(
    description='Clear description of what tool does',
    formatter_class=argparse.RawDescriptionHelpFormatter,
    epilog='Detailed examples here'
)

# Required arguments first
parser.add_argument('input_file', help='Input file to process')

# Optional with sensible defaults
parser.add_argument('--output', default='output.txt',
                   help='Output file (default: output.txt)')

# Validate arguments
args = parser.parse_args()
if args.dpi < 72:
    parser.error("--dpi must be >= 72")
```

### 2. Progress Feedback

Users need to know what's happening:

```python
print(f"Converting {pdf_path.name} to images (DPI={dpi})...")
print(f"Total pages in PDF: {total_pages}")

for i, image in enumerate(images, start=1):
    print(f"Processing page {i}/{total_pages}...", end=' ', flush=True)
    result = process(image)
    print(f"✓ ({elapsed:.1f}s)")
```

### 3. Timing & Statistics

Help users understand performance:

```python
start_time = time.time()

# ... processing ...

total_time = time.time() - start_time
print(f"\nDone! Processed {count} page(s) in {total_time:.1f}s")
print(f"Average: {total_time/count:.1f}s per page")
```

### 4. Verbose Mode

Provide debugging information when needed:

```python
if verbose:
    print(f"Input: {pdf_path}")
    print(f"Model: {model}")
    print(f"Prompt: {prompt_type} -> '{ocr_prompt}'")
```

---

## Error Handling & Resilience

### 1. Graceful Degradation

Continue processing even when individual items fail:

```python
for i, page in enumerate(pages):
    try:
        result = process_page(page)
        results.append(result)
    except Exception as e:
        print(f"Warning: Page {i} failed: {e}", file=sys.stderr)
        results.append(f"*Processing failed for page {i}*")
        continue  # Don't stop entire job
```

### 2. Resource Cleanup

Always clean up temporary resources:

```python
with tempfile.TemporaryDirectory() as temp_dir:
    # Processing here
    # Automatically cleaned up even if error occurs
    pass
```

### 3. Rate Limiting

Prevent overloading external services:

```python
for page in pages:
    result = process(page)
    if delay > 0:
        time.sleep(delay)  # Configurable delay
```

### 4. Retry Logic

For transient failures:

```python
def retry_with_backoff(func, max_retries=3, base_delay=2):
    """Retry with exponential backoff."""
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            delay = base_delay ** attempt
            print(f"Retry {attempt + 1}/{max_retries} after {delay}s...")
            time.sleep(delay)
```

---

## Performance Optimization

### 1. Lazy Loading

Load resources only when needed:

```python
# Good: Load on demand
images = convert_from_path(pdf_path, dpi=dpi)
images = images[start_idx:end_idx]  # Then slice

# Bad: Load all then filter
all_images = convert_from_path(pdf_path, dpi=dpi)  # Loads all 1000 pages
filtered = all_images[:10]  # Only need 10
```

### 2. Batch Processing

Process multiple items efficiently:

```python
# Process all images in directory
for img_path in image_dir.glob('*.png'):
    results.append(process_image(img_path))
```

### 3. Caching

Avoid redundant work:

```python
@lru_cache(maxsize=128)
def load_model(model_name):
    """Cache loaded models."""
    return expensive_model_load(model_name)
```

---

## Testing & Validation

### 1. Input Validation

Validate early and thoroughly:

```python
# Check file exists
if not path.exists():
    raise FileNotFoundError(f"File not found: {path}")

# Check file type
if path.suffix.lower() not in ['.pdf', '.png', '.jpg']:
    raise ValueError(f"Unsupported file type: {path.suffix}")

# Check argument ranges
if dpi < 72 or dpi > 1200:
    raise ValueError(f"DPI must be between 72-1200, got {dpi}")
```

### 2. Test Data

Include representative test files:

```
tests/
├── test_simple.pdf       # 1 page, clean text
├── test_complex.pdf      # Multi-column, images
├── test_handwritten.pdf  # Handwriting
└── test_multilang.pdf    # Multiple languages
```

### 3. Edge Cases

Test boundary conditions:

```python
# Test with:
# - Empty PDF (0 pages)
# - Single page
# - Very large PDF (1000+ pages)
# - Corrupted PDF
# - PDF with no text
# - PDF with only images
```

### 4. Integration Tests

Test the full pipeline:

```python
def test_full_pipeline():
    """Test complete OCR workflow."""
    result = ocr_pdf('test.pdf', 'output.txt', dpi=300)
    assert Path('output.txt').exists()
    content = Path('output.txt').read_text()
    assert len(content) > 0
    assert 'expected text' in content
```

---

## Documentation

### 1. README Structure

Essential sections:

```markdown
# Project Name

## Quick Start (< 5 minutes)
- Installation
- Basic usage example

## Installation & Setup
- Detailed installation for all platforms
- Dependencies
- Verification steps

## Usage Examples
- Common use cases
- Command-line options
- API reference (if applicable)

## Troubleshooting
- Common issues and solutions

## Contributing
- How to contribute
- Development setup

## License
```

### 2. Code Documentation

```python
def ocr_pdf(
    pdf_path: str,
    output_path: str = "output.txt",
    dpi: int = 300,
    start_page: int = 1,
    end_page: Optional[int] = None
) -> None:
    """
    Perform OCR on a PDF file.

    Args:
        pdf_path: Path to input PDF file
        output_path: Path to output text file (default: output.txt)
        dpi: Resolution for PDF to image conversion (default: 300)
        start_page: First page to process, 1-indexed (default: 1)
        end_page: Last page to process, inclusive (default: all pages)

    Raises:
        FileNotFoundError: If pdf_path doesn't exist
        ValueError: If start_page > end_page or dpi < 72

    Example:
        >>> ocr_pdf('document.pdf', 'output.txt', dpi=400)
        Processing pages 1 to 10 (10 page(s))
        Done! Output saved to: output.txt
    """
```

### 3. Help Text

Make `--help` genuinely helpful:

```python
parser = argparse.ArgumentParser(
    description='OCR multi-page PDFs using DeepSeek-OCR via Ollama',
    epilog="""
Examples:
  # Basic usage
  %(prog)s document.pdf

  # Process first 10 pages
  %(prog)s document.pdf --end-page 10

  # High quality markdown output
  %(prog)s document.pdf --dpi 400 --prompt markdown
    """
)
```

---

## Security Considerations

### 1. Input Sanitization

Never trust user input:

```python
# Validate file paths
pdf_path = Path(pdf_path).resolve()  # Resolve to absolute path
if not pdf_path.exists():
    raise FileNotFoundError(f"File not found: {pdf_path}")

# Prevent path traversal
if ".." in str(pdf_path):
    raise ValueError("Path traversal not allowed")
```

### 2. Command Injection Prevention

Be careful with subprocess calls:

```python
# Good: Use list arguments
subprocess.run(['ollama', 'run', model, prompt])

# Bad: Shell injection risk
subprocess.run(f'ollama run {model} "{prompt}"', shell=True)
```

### 3. Resource Limits

Prevent resource exhaustion:

```python
# Limit file size
max_size = 100 * 1024 * 1024  # 100MB
if pdf_path.stat().st_size > max_size:
    raise ValueError(f"File too large (max {max_size} bytes)")

# Limit pages processed
if end_page and end_page > 1000:
    raise ValueError("Cannot process more than 1000 pages at once")
```

---

## Common Pitfalls

### 1. ❌ Ignoring Exit Codes

```python
# Bad
result = subprocess.run(['command'])
# Continues even if command failed

# Good
result = subprocess.run(['command'], check=True)
# Raises exception on failure
```

### 2. ❌ Poor Progress Indication

```python
# Bad: No feedback
for page in pages:
    process(page)

# Good: Clear progress
for i, page in enumerate(pages, 1):
    print(f"Processing {i}/{len(pages)}...", flush=True)
    process(page)
```

### 3. ❌ Hardcoded Values

```python
# Bad
def process(file):
    dpi = 300  # Hardcoded
    model = 'deepseek-ocr'  # Hardcoded

# Good
def process(file, dpi=300, model='deepseek-ocr'):
    # Configurable with sensible defaults
```

### 4. ❌ Silent Failures

```python
# Bad
try:
    result = risky_operation()
except:
    pass  # Silently fails

# Good
try:
    result = risky_operation()
except Exception as e:
    print(f"Error: {e}", file=sys.stderr)
    raise
```

---

## Specific Patterns

### Pattern 1: Page Range Processing

```python
# Convert to 0-indexed
start_idx = max(0, start_page - 1)
end_idx = min(total_pages, end_page) if end_page else total_pages

# Validate
if start_idx >= total_pages:
    raise ValueError(f"Start page {start_page} exceeds total ({total_pages})")

# Slice and process
pages = all_pages[start_idx:end_idx]
```

### Pattern 2: Output Formatting

```python
# Include metadata in output
with open(output_path, 'w') as f:
    f.write(f"# OCR Results: {input_file.name}\n")
    f.write(f"# Date: {datetime.now().isoformat()}\n")
    f.write(f"# Pages: {start_page}-{end_page}\n")
    f.write(f"# Model: {model}\n\n")
    f.writelines(results)
```

### Pattern 3: Configuration Management

```python
# Centralized configuration
@dataclass
class OCRConfig:
    dpi: int = 300
    model: str = 'deepseek-ocr'
    delay: int = 0
    verbose: bool = False

    def validate(self):
        if self.dpi < 72:
            raise ValueError("DPI must be >= 72")
        if self.delay < 0:
            raise ValueError("Delay must be >= 0")
```

### Pattern 4: Logging

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Use throughout code
logger.info(f"Processing {pdf_path}")
logger.warning(f"Page {i} took {elapsed:.1f}s (slow)")
logger.error(f"Failed to process page {i}: {error}")
```

---

## Summary Checklist

### Before Release

- [ ] All CLI arguments have helpful descriptions
- [ ] `--help` output is clear and includes examples
- [ ] Input validation for all user inputs
- [ ] Error messages are actionable
- [ ] Progress feedback for long operations
- [ ] Timing statistics provided
- [ ] README includes installation, usage, and examples
- [ ] Tested on edge cases (empty, large, corrupted files)
- [ ] Resource cleanup (temp files, connections)
- [ ] Exit codes are meaningful
- [ ] No hardcoded credentials or secrets
- [ ] Verbose/debug mode available
- [ ] Graceful handling of Ctrl+C

### Code Quality

- [ ] Functions have clear docstrings
- [ ] Type hints where appropriate
- [ ] No overly complex functions (< 50 lines)
- [ ] DRY principle followed
- [ ] Meaningful variable names
- [ ] Consistent code style
- [ ] No commented-out code

---

## Additional Resources

- **Python CLI Best Practices**: https://click.palletsprojects.com/
- **Argparse Tutorial**: https://docs.python.org/3/howto/argparse.html
- **Error Handling**: https://docs.python.org/3/tutorial/errors.html
- **Testing**: https://docs.pytest.org/
- **Type Hints**: https://docs.python.org/3/library/typing.html

---

*Last updated: January 2026*
