import asyncio
import argparse
import os
from pathlib import Path
from loguru import logger
import sys

# Add project root to import path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app.core.worflow import get_workflow


def validate_file(file_path: str) -> bool:
    """Check if file exists"""
    if not os.path.exists(file_path):
        logger.error(f"❌ File not found: {file_path}")
        return False
    return True


def detect_input_type(value: str) -> str:
    """Detect if input is text, pdf, or image path"""
    if os.path.exists(value):
        ext = Path(value).suffix.lower()
        if ext == ".pdf":
            return "pdf"
        if ext in [".jpg", ".jpeg", ".png", ".webp", ".bmp", ".gif"]:
            return "image"
        return "unknown_file"
    return "text"


async def run_text_test(text: str, session_id: str, user_id: str, language: str):
    logger.info("📝 Running workflow with TEXT input...")
    
    workflow = get_workflow()
    
    response = await workflow.run_conversation(
        user_input=text,
        session_id=session_id,
        user_id=user_id,
        language=language,
        image_url=None,
        pdf_url=None,
        audio_url=None
    )
    
    print("\n" + "="*70)
    print("✅ TEXT INPUT RESPONSE")
    print("="*70)
    print(f"User Input: {text}\n")
    print(f"Assistant Response:\n{response.get('assistant_response', '❌ No response')}")
    print("="*70)


async def run_pdf_test(pdf_path: str, session_id: str, user_id: str, language: str):
    logger.info("📄 Running workflow with PDF input...")

    workflow = get_workflow()
    abs_pdf = os.path.abspath(pdf_path)

    response = await workflow.run_conversation(
        user_input="Please analyze this PDF document",
        session_id=session_id,
        user_id=user_id,
        language=language,
        image_url=None,
        pdf_url=abs_pdf,
        audio_url=None
    )
    
    print("\n" + "="*70)
    print("✅ PDF INPUT RESPONSE")
    print("="*70)
    print(f"PDF Path: {pdf_path}\n")
    print(f"Assistant Response:\n{response.get('assistant_response', '❌ No response')}")
    print("="*70)


async def run_image_test(image_path: str, session_id: str, user_id: str, language: str):
    logger.info("🖼️ Running workflow with IMAGE input...")

    workflow = get_workflow()
    abs_img = os.path.abspath(image_path)

    response = await workflow.run_conversation(
        user_input="Please analyze this medical image / report",
        session_id=session_id,
        user_id=user_id,
        language=language,
        image_url=abs_img,
        pdf_url=None,
        audio_url=None
    )

    print("\n" + "="*70)
    print("✅ IMAGE INPUT RESPONSE")
    print("="*70)
    print(f"Image Path: {image_path}\n")
    print(f"Assistant Response:\n{response.get('assistant_response', '❌ No response')}")
    print("="*70)


async def main():
    parser = argparse.ArgumentParser(
        description="Test Medical Assistant Workflow with text, PDF, or image"
    )

    parser.add_argument(
        "--input",
        type=str,
        required=True,
        help="Text message OR path to PDF/image"
    )
    
    parser.add_argument("--session-id", default="test_session_001")
    parser.add_argument("--user-id", default="test_user_123")
    parser.add_argument("--language", default="en", choices=["en", "kn", "hi"])

    args = parser.parse_args()

    input_type = detect_input_type(args.input)

    if input_type == "pdf":
        if not validate_file(args.input):
            return
        await run_pdf_test(args.input, args.session_id, args.user_id, args.language)

    elif input_type == "image":
        if not validate_file(args.input):
            return
        await run_image_test(args.input, args.session_id, args.user_id, args.language)

    elif input_type == "text":
        await run_text_test(args.input, args.session_id, args.user_id, args.language)

    else:
        logger.error("❌ Unsupported file type. Provide text, a .pdf, or an image file.")


if __name__ == "__main__":
    asyncio.run(main())




#python workflow_test.py --input "D:/mini/fake_medical_report_for_testing.pdf"

#python workflow_test.py --input "D:/mini/sample_prescription.jpg"

#python workflow_test.py --input "I have a headache, what should I do?"
