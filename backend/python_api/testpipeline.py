import sys
import asyncio
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from fastapi import UploadFile

# Import services to test directly
from services.ocr_services import extract_text_from_document
from services.request_validation import validate_document_input
from services.validation_services import validate_passport_fields
from services.orchestration_service import run_full_pipeline


def create_mock_passport_image() -> BytesIO:
    """Generates a sample passport-like image in memory for testing."""
    img = Image.new("RGB", (600, 400), color=(240, 240, 240))
    d = ImageDraw.Draw(img)
    
    # Draw mock passport text
    d.text((30, 30), "REPUBLIC OF INDIA", fill=(0, 0, 0))
    d.text((30, 80), "PASSPORT NO: Z1234567", fill=(0, 0, 0))
    d.text((30, 130), "NATIONALITY: IND", fill=(0, 0, 0))
    d.text((30, 180), "DATE OF BIRTH: 15/08/1995", fill=(0, 0, 0))
    d.text((30, 230), "EXPIRY DATE: 20/10/2030", fill=(0, 0, 0))
    
    img_byte_arr = BytesIO()
    img.save(img_byte_arr, format="JPEG")
    img_byte_arr.seek(0)
    return img_byte_arr


async def run_tests():
    print("=" * 60)
    print("      RUNNING BACKEND PIPELINE & SERVICE DIAGNOSTICS      ")
    print("=" * 60)

    # 1. Generate test image binary stream
    image_stream = create_mock_passport_image()
    mock_file = UploadFile(
        filename="test_passport.jpg",
        file=image_stream,
        headers={"content-type": "image/jpeg"}
    )

    # Test 1: Input Validation Service
    print("\n[1/4] Testing File Input Validation...")
    try:
        val_res = await validate_document_input(mock_file)
        print(f"  ✓ SUCCESS: File validated ({val_res['size_bytes']} bytes)")
    except Exception as e:
        print(f"  ✗ FAILED: {e}")

    # Test 2: Local Tesseract OCR Extraction
    print("\n[2/4] Testing Local Tesseract OCR Engine...")
    try:
        ocr_res = await extract_text_from_document(mock_file)
        print(f"  ✓ SUCCESS: Provider = {ocr_res['provider']}")
        print(f"    - Extracted Text Snippet: {repr(ocr_res['raw_text'][:40])}...")
        print(f"    - Parsed Fields: {list(ocr_res['fields'].keys())}")
    except Exception as e:
        print(f"  ✗ FAILED: {e}")

    # Test 3: Passport Field Rules Engine
    print("\n[3/4] Testing Passport Field Validation Rules...")
    try:
        mock_fields = {"DocumentNumber": {"value": "Z1234567"}, "CountryRegion": {"value": "IND"}}
        rule_res = validate_passport_fields(mock_fields)
        print(f"  ✓ SUCCESS: Validation Score = {rule_res['validation_score']}/100")
        print(f"    - Errors Found: {len(rule_res['errors'])}")
    except Exception as e:
        print(f"  ✗ FAILED: {e}")

    # Test 4: End-to-End Orchestrated Pipeline
    print("\n[4/4] Testing Full Orchestration Pipeline...")
    try:
        # Reset image stream position for pipeline run
        image_stream.seek(0)
        pipeline_file = UploadFile(
            filename="test_passport.jpg",
            file=image_stream,
            headers={"content-type": "image/jpeg"}
        )
        pipeline_res = await run_full_pipeline(document_file=pipeline_file)
        print(f"  ✓ SUCCESS: Pipeline Executed!")
        print(f"    - Final Risk Score : {pipeline_res['risk_score']}/100")
        print(f"    - Final Verdict    : {pipeline_res['verdict']}")
        print(f"    - Storage Saved Path: {pipeline_res['file_path']}")
    except Exception as e:
        print(f"  ✗ FAILED: {e}")

    print("\n" + "=" * 60)
    print("                  DIAGNOSTICS COMPLETE                    ")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(run_tests())