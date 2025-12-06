# Medical Assistant Workflow Test

This test file allows you to test the medical assistant workflow with different input types: text, images, and PDF documents.

## Features

- **Text Input**: Send text queries to the medical assistant
- **Image Input**: Analyze medical images (X-rays, scans, etc.)
- **PDF Input**: Analyze medical documents (reports, prescriptions, etc.)
- **Multi-language Support**: English (en), Kannada (kn), Hindi (hi)

## Usage

### Basic Text Query

```bash
python workflow_test.py --text "I have a headache, what should I do?"
```

### Using Images

```bash
python workflow_test.py --image "/path/to/medical_image.jpg"
```

Supported image formats: `.jpg`, `.jpeg`, `.png`, `.gif`, `.webp`, `.bmp`

### Using PDF Documents

```bash
python workflow_test.py --pdf "/path/to/medical_report.pdf"
```

### With Different Languages

**Kannada:**
```bash
python workflow_test.py --text "ನನಗೆ ತಲೆನೋವು ಇದೆ" --language kn
```

**Hindi:**
```bash
python workflow_test.py --text "मुझे सिरदर्द है" --language hi
```

### Custom Session and User ID

```bash
python workflow_test.py \
  --text "Describe my symptoms" \
  --session-id "session_123" \
  --user-id "user_456" \
  --language en
```

## Command-Line Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `--text` | Text input for the medical assistant | None |
| `--image` | Path to image file | None |
| `--pdf` | Path to PDF file | None |
| `--session-id` | Session ID for the conversation | `test_session_001` |
| `--user-id` | User ID for the conversation | `test_user_123` |
| `--language` | Language code (en/kn/hi) | `en` |

## Examples

### Example 1: Analyze an X-ray image
```bash
python workflow_test.py --image "data/xray_image.jpg" --language en
```

### Example 2: Analyze a medical report PDF
```bash
python workflow_test.py --pdf "reports/patient_report.pdf" --language en
```

### Example 3: Ask a medical question in Kannada
```bash
python workflow_test.py --text "ರಕ್ತದ ಒತ್ತಡ ವಿಶೇಷಣೆ" --language kn
```

### Example 4: Default test (no arguments)
```bash
python workflow_test.py
```
This runs a default text test: "Hello! I have a headache, what should I do?"

## Output

The test will display:
- Input type (Text/Image/PDF)
- The input content or file path
- The medical assistant's response
- Session and conversation details

## Notes

- Only one input type can be used at a time (text, image, or PDF)
- Images are analyzed using Google's Gemini Vision API
- PDF documents are processed using pdfplumber for text extraction
- Text queries are processed by the MedGemma medical language model
- All file paths should be absolute or relative to the current directory
