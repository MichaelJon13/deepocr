# Code Review Against agents.md Best Practices

*Review Date: January 9, 2026*

## Summary

Overall, the repository follows most best practices from agents.md. The code is well-structured, uses argparse correctly, has good error handling, and comprehensive documentation. However, there are several improvements that would enhance robustness, maintainability, and user experience.

## ✅ What's Working Well

1. **CLI Design** - Excellent argparse implementation with clear help text
2. **Progress Feedback** - Real-time progress with timing statistics
3. **Error Handling** - Graceful degradation when pages fail
4. **Resource Cleanup** - Proper use of tempfile.TemporaryDirectory
5. **Documentation** - Comprehensive README with examples
6. **Input Validation** - Good argument validation
7. **Verbose Mode** - Helpful debugging information
8. **Security** - Uses list arguments for subprocess (prevents injection)

---

## 🔴 High Priority Improvements

### 1. Add Type Hints (agents.md: Code Quality)

**Current:**
```python
def ocr_pdf(
    pdf_path,
    output_path="output.txt",
    dpi=300,
    ...
):
```

**Recommended:**
```python
from typing import Optional

def ocr_pdf(
    pdf_path: str,
    output_path: str = "output.txt",
    dpi: int = 300,
    delay: int = 0,
    start_page: int = 1,
    end_page: Optional[int] = None,
    prompt_type: str = 'free',
    model: str = 'deepseek-ocr',
    verbose: bool = False
) -> None:
```

**Impact:** Better IDE support, catches type errors early, improves code documentation

---

### 2. Add Resource Limits (agents.md: Security Considerations)

**Issue:** No limits on file size or page count could lead to resource exhaustion

**Recommended Addition:**
```python
# Add to argument parser
parser.add_argument(
    '--max-pages',
    type=int,
    default=500,
    help='Maximum pages to process in one run (default: 500)'
)

# Add to validation
MAX_FILE_SIZE = 500 * 1024 * 1024  # 500MB
file_size = pdf_path.stat().st_size
if file_size > MAX_FILE_SIZE:
    parser.error(f"File too large: {file_size/1024/1024:.1f}MB (max 500MB)")

pages_to_process = (end_page or total_pages) - start_page + 1
if pages_to_process > args.max_pages:
    parser.error(f"Too many pages: {pages_to_process} (max {args.max_pages})")
```

**Impact:** Prevents system crashes from processing massive files

---

### 3. Add requirements.txt/pyproject.toml (agents.md: Documentation)

**Issue:** No dependency file for reproducible installations

**Recommended: requirements.txt**
```txt
pdf2image>=1.16.0
Pillow>=10.0.0
```

**Or pyproject.toml:**
```toml
[project]
name = "deepocr"
version = "1.0.0"
description = "OCR multi-page PDFs using DeepSeek-OCR via Ollama"
requires-python = ">=3.8"
dependencies = [
    "pdf2image>=1.16.0",
    "Pillow>=10.0.0",
]

[project.scripts]
deepocr = "app:main"
```

**Impact:** Makes installation easier and more reliable

---

### 4. Better Lazy Loading (agents.md: Performance Optimization)

**Current Issue:** Loads ALL pages into memory, then slices

**Current Code:**
```python
images = convert_from_path(pdf_path, dpi=dpi)  # Loads all 179 pages
# ...
images = images[start_idx:end_idx]  # Then slices to 10
```

**Recommended:**
```python
# Use first_page and last_page parameters
images = convert_from_path(
    pdf_path,
    dpi=dpi,
    first_page=start_page,
    last_page=end_page
)
```

**Impact:** Massive memory savings for large PDFs (179 pages → 10 pages loaded)

---

## 🟡 Medium Priority Improvements

### 5. Add Retry Logic for Transient Failures (agents.md: Error Handling)

**Recommended Addition:**
```python
def run_ocr_with_retry(img_path, ocr_prompt, model, max_retries=3):
    """Run OCR with exponential backoff retry."""
    for attempt in range(max_retries):
        result = subprocess.run(
            ["ollama", "run", model, f"{str(img_path)}\n{ocr_prompt}"],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            return result

        if attempt < max_retries - 1:
            delay = 2 ** attempt  # 1s, 2s, 4s
            print(f"  Retry {attempt + 1}/{max_retries - 1} in {delay}s...",
                  file=sys.stderr)
            time.sleep(delay)

    return result  # Return failed result after all retries
```

**Impact:** More resilient to temporary Ollama hiccups

---

### 6. Add Logging Module (agents.md: Specific Patterns)

**Current:** Uses print statements
**Recommended:** Use logging module

```python
import logging

# Setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('ocr.log') if verbose else logging.NullHandler()
    ]
)
logger = logging.getLogger(__name__)

# Usage
logger.info(f"Processing {pdf_path}")
logger.warning(f"Page {i} took {elapsed:.1f}s")
logger.error(f"OCR failed: {result.stderr}")
```

**Impact:** Better debugging, log rotation, filtering by level

---

### 7. Add File Type Validation (agents.md: Testing & Validation)

**Recommended Addition:**
```python
# After resolving path
if not pdf_path.suffix.lower() == '.pdf':
    print(f"Error: Expected PDF file, got {pdf_path.suffix}", file=sys.stderr)
    sys.exit(1)

# Check if it's actually a PDF (magic bytes)
with open(pdf_path, 'rb') as f:
    magic = f.read(4)
    if magic != b'%PDF':
        print(f"Error: File is not a valid PDF", file=sys.stderr)
        sys.exit(1)
```

**Impact:** Better error messages for wrong file types

---

### 8. Add Prompt Versioning (agents.md: Prompt Engineering)

**Recommended:**
```python
PROMPT_VERSION = "1.0"

OCR_PROMPTS = {
    'free': {
        'prompt': 'Free OCR.',
        'version': '1.0',
        'description': 'Simple text extraction'
    },
    'layout': {
        'prompt': '<|grounding|>Given the layout of the image.',
        'version': '1.0',
        'description': 'Layout-aware parsing'
    },
    # ...
}

# In output metadata
f.write(f"# Prompt Version: {PROMPT_VERSION}\n")
```

**Impact:** Track which prompt versions produced which results

---

### 9. Add JSON Output Format Option (agents.md: Tool Design)

**Recommended Addition:**
```python
parser.add_argument(
    '--format',
    choices=['text', 'json'],
    default='text',
    help='Output format (default: text)'
)

# When writing output
if args.format == 'json':
    import json
    output_data = {
        'metadata': {
            'input': pdf_path.name,
            'pages': f"{start_page}-{end_page}",
            'model': model,
            'prompt': prompt_type,
            'timestamp': datetime.now().isoformat()
        },
        'results': [
            {'page': i, 'text': text, 'status': 'success'}
            for i, text in enumerate(results, start=start_page)
        ]
    }
    json.dump(output_data, f, indent=2)
```

**Impact:** Machine-readable output for downstream processing

---

## 🟢 Low Priority / Nice to Have

### 10. Add Progress Bar (agents.md: Tool Design)

**Current:** Text-based progress
**Recommended:** Visual progress bar using tqdm

```python
from tqdm import tqdm

for image in tqdm(images, desc="OCR Progress", unit="page"):
    # ... processing
```

**Impact:** Better visual feedback, but requires extra dependency

---

### 11. Add Configuration File Support

**Recommended:**
```python
# Support .deepocr.yaml config file
import yaml

def load_config(config_path='~/.deepocr.yaml'):
    """Load configuration from YAML file."""
    path = Path(config_path).expanduser()
    if path.exists():
        with open(path) as f:
            return yaml.safe_load(f)
    return {}

# Merge config with CLI args (CLI takes precedence)
```

**Impact:** Easier for repeated use with same settings

---

### 12. Add Dry-Run Mode

**Recommended:**
```python
parser.add_argument(
    '--dry-run',
    action='store_true',
    help='Show what would be processed without actually running OCR'
)

if args.dry_run:
    print(f"Would process: {pdf_path}")
    print(f"Pages: {start_page} to {end_page}")
    print(f"Total pages: {len(images)}")
    print(f"Estimated time: ~{len(images) * 12}s")
    sys.exit(0)
```

**Impact:** Test configuration before long runs

---

### 13. Add Checkpointing for Long Jobs

**Recommended:**
```python
# Save progress periodically
checkpoint_file = output_path.with_suffix('.checkpoint.json')

# Resume from checkpoint
if checkpoint_file.exists() and args.resume:
    with open(checkpoint_file) as f:
        completed_pages = json.load(f)['completed']
```

**Impact:** Resume interrupted jobs without starting over

---

### 14. Add Signal Handling for Graceful Shutdown

**Recommended:**
```python
import signal

def signal_handler(signum, frame):
    print("\n\nInterrupted! Saving partial results...", file=sys.stderr)
    # Write partial results
    with open(output_path, 'w') as f:
        f.write("# Partial results (interrupted)\n")
        f.writelines(results)
    print(f"Partial results saved to {output_path}")
    sys.exit(1)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)
```

**Impact:** Don't lose work on Ctrl+C

---

## 📋 Repository Structure Improvements

### 15. Add Missing Files

**Recommended File Structure:**
```
deepocr/
├── .gitignore          # ❌ Missing
├── LICENSE             # ❌ Missing
├── README.md           # ✅ Present
├── agents.md           # ✅ Present
├── requirements.txt    # ❌ Missing
├── app.py              # ✅ Present
├── 179pageExample.pdf  # ✅ Present
├── tests/              # ❌ Missing
│   ├── __init__.py
│   ├── test_app.py
│   └── fixtures/
│       └── test.pdf
└── examples/           # ❌ Missing
    └── sample_output.txt
```

---

### 16. Add .gitignore

**Recommended .gitignore:**
```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.venv/
*.egg-info/
dist/
build/

# OCR outputs
output.txt
output.md
*.checkpoint.json
ocr.log

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Temp files
*.tmp
temp/
```

---

### 17. Add Simple Tests

**Recommended: tests/test_app.py**
```python
import pytest
from pathlib import Path
from app import ocr_pdf

def test_input_validation():
    """Test that invalid inputs are rejected."""
    with pytest.raises(SystemExit):
        ocr_pdf('nonexistent.pdf')

def test_page_range():
    """Test page range selection."""
    # Use 179pageExample.pdf
    output = Path('test_output.txt')
    ocr_pdf('179pageExample.pdf', str(output), start_page=1, end_page=2)

    assert output.exists()
    content = output.read_text()
    assert 'Page 1' in content
    assert 'Page 2' in content

    output.unlink()  # Cleanup
```

---

## 🎯 Implementation Priority

### Phase 1 (Do First)
1. ✅ Add type hints
2. ✅ Add requirements.txt
3. ✅ Add .gitignore
4. ✅ Fix lazy loading (use first_page/last_page)
5. ✅ Add resource limits

### Phase 2 (Do Soon)
6. Add retry logic
7. Add file type validation
8. Add logging module
9. Add prompt versioning

### Phase 3 (Nice to Have)
10. Add JSON output format
11. Add tests
12. Add signal handling
13. Add progress bar (tqdm)

### Phase 4 (Future)
14. Add config file support
15. Add checkpointing
16. Add dry-run mode

---

## Summary Statistics

**Checklist from agents.md:**

### Before Release
- ✅ All CLI arguments have helpful descriptions
- ✅ `--help` output is clear and includes examples
- ⚠️ Input validation for all user inputs (missing file type, size checks)
- ✅ Error messages are actionable
- ✅ Progress feedback for long operations
- ✅ Timing statistics provided
- ✅ README includes installation, usage, and examples
- ❌ Tested on edge cases (need test suite)
- ✅ Resource cleanup (temp files, connections)
- ✅ Exit codes are meaningful
- ❌ No hardcoded credentials or secrets (N/A)
- ✅ Verbose/debug mode available
- ⚠️ Graceful handling of Ctrl+C (could be better)

### Code Quality
- ⚠️ Functions have clear docstrings (present but no type hints)
- ❌ Type hints where appropriate
- ✅ No overly complex functions
- ✅ DRY principle followed
- ✅ Meaningful variable names
- ✅ Consistent code style
- ✅ No commented-out code

**Score: 13/20 Complete, 4/20 Partial, 3/20 Missing**

---

## Recommendations

**Minimum viable improvements:**
- Add type hints (5 min)
- Add requirements.txt (2 min)
- Add .gitignore (2 min)
- Fix lazy loading (5 min)
- Add basic resource limits (10 min)

**Total time: ~25 minutes for significant quality boost**

---

*End of Review*
