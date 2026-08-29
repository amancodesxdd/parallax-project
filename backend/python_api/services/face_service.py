import logging
import os

import boto3
from botocore.exceptions import BotoCoreError, ClientError
from fastapi import UploadFile
from dotenv import load_dotenv


load_dotenv()

logger = logging.getLogger(__name__)


AWS_REGION = os.getenv(
    "AWS_REGION",
    "ap-south-1"
)

AWS_COLLECTION_ID = os.getenv(
    "AWS_REKOGNITION_COLLECTION_ID",
    "parralax-face-collection"
)


rekognition = boto3.client(
    "rekognition",
    region_name=AWS_REGION
)


async def verify_face(
    document: UploadFile,
    selfie: UploadFile
):
    """
    Person 4 - Task 3

    Compare the face in the document image with
    the submitted selfie using AWS Rekognition.

    This function returns normal Python data so that
    Person 5 does not need to interact directly
    with the AWS SDK.
    """

    if document is None:
        raise ValueError(
            "Document image is required."
        )

    if selfie is None:
        raise ValueError(
            "Selfie image is required."
        )

    if not document.filename:
        raise ValueError(
            "Document filename is missing."
        )

    if not selfie.filename:
        raise ValueError(
            "Selfie filename is missing."
        )

    document_bytes = await document.read()
    selfie_bytes = await selfie.read()

    if not document_bytes:
        raise ValueError(
            "Document image is empty."
        )

    if not selfie_bytes:
        raise ValueError(
            "Selfie image is empty."
        )

    logger.info(
        "Starting AWS face verification"
    )

    try:

        response = rekognition.compare_faces(
            SourceImage={
                "Bytes": document_bytes
            },
            TargetImage={
                "Bytes": selfie_bytes
            },
            SimilarityThreshold=80
        )

        face_matches = response.get(
            "FaceMatches",
            []
        )

        unmatched_faces = response.get(
            "UnmatchedFaces",
            []
        )

        if not face_matches:

            return {
                "provider": "aws-rekognition",
                "matched": False,
                "face_score": 0.0,
                "confidence": 0.0,
                "message": (
                    "No matching face was detected."
                ),
                "matches": [],
                "unmatched_faces": len(
                    unmatched_faces
                )
            }

        best_match = max(
            face_matches,
            key=lambda match: match.get(
                "Similarity",
                0
            )
        )

        similarity = float(
            best_match.get(
                "Similarity",
                0
            )
        )

        confidence = float(
            best_match.get(
                "Face",
                {}
            ).get(
                "Confidence",
                0
            )
        )

        matched = similarity >= 80

        logger.info(
            "Face verification completed. "
            "Similarity=%s",
            similarity
        )

        return {
            "provider": "aws-rekognition",
            "matched": matched,
            "face_score": similarity,
            "confidence": confidence,
            "message": (
                "Face verification successful."
                if matched
                else
                "Face similarity is below the threshold."
            ),
            "matches": [
                {
                    "similarity": similarity,
                    "confidence": confidence
                }
            ],
            "unmatched_faces": len(
                unmatched_faces
            )
        }

    except (BotoCoreError, ClientError) as exc:

        logger.exception(
            "AWS Rekognition request failed"
        )

        raise RuntimeError(
            "AWS face verification failed."
        ) from exc