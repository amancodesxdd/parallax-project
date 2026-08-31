import asyncio
import io
import os

from fastapi import UploadFile

from services.face_service import verify_face_match

TESTDATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "testdata")


def load_upload(name: str) -> UploadFile:
    with open(os.path.join(TESTDATA, name), "rb") as f:
        return UploadFile(filename=name, file=io.BytesIO(f.read()))


async def run_tests():
    print("=" * 60)
    print("      FACE MATCHING (MULTI-CHANNEL HISTOGRAM) TESTS      ")
    print("=" * 60)

    cases = [
        ("lena.jpg", "lena.jpg", "SAME image (same person)"),
        ("lena.jpg", "messi5.jpg", "DIFFERENT people"),
    ]

    for doc, selfie, label in cases:
        res = await verify_face_match(load_upload(doc), load_upload(selfie))
        print(f"\n[{label}]")
        print(f"  doc={doc}  selfie={selfie}")
        print(f"  face_score={res['face_score']}  matched={res['matched']}")
        print(f"  details: {res.get('details') or res.get('error')}")


if __name__ == "__main__":
    asyncio.run(run_tests())