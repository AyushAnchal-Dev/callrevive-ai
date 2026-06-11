"""
CallRevive AI — Storage service.

Backblaze B2 (S3-compatible) for call recordings and file uploads.
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone

import boto3
from botocore.config import Config as BotoConfig
from botocore.exceptions import ClientError

from app.core.config import Settings, get_settings

logger = logging.getLogger(__name__)


class StorageService:
    """S3-compatible client for Backblaze B2 object storage."""

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()
        self._client = boto3.client(
            "s3",
            endpoint_url=self._settings.BACKBLAZE_ENDPOINT_URL,
            aws_access_key_id=self._settings.BACKBLAZE_KEY_ID,
            aws_secret_access_key=self._settings.BACKBLAZE_APPLICATION_KEY,
            config=BotoConfig(
                signature_version="s3v4",
                retries={"max_attempts": 3, "mode": "standard"},
            ),
        )
        self._bucket = self._settings.BACKBLAZE_BUCKET_NAME

    async def upload_file(
        self,
        file_content: bytes,
        file_name: str,
        content_type: str = "application/octet-stream",
    ) -> str:
        """
        Upload a file to B2 and return its storage key.

        The storage key is a UUID-prefixed path to avoid collisions.
        """
        # Generate unique storage key
        date_prefix = datetime.now(timezone.utc).strftime("%Y/%m/%d")
        unique_id = uuid.uuid4().hex[:12]
        storage_key = f"{date_prefix}/{unique_id}_{file_name}"

        try:
            self._client.put_object(
                Bucket=self._bucket,
                Key=storage_key,
                Body=file_content,
                ContentType=content_type,
            )
            logger.info(
                "Uploaded file to B2: bucket=%s key=%s size=%d",
                self._bucket,
                storage_key,
                len(file_content),
            )
            return storage_key
        except ClientError as exc:
            logger.error("Failed to upload file to B2: %s", exc)
            raise

    async def get_download_url(
        self,
        storage_key: str,
        expires_in: int = 3600,
    ) -> str:
        """
        Generate a pre-signed download URL for a stored file.

        Default expiration: 1 hour.
        """
        try:
            url = self._client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self._bucket, "Key": storage_key},
                ExpiresIn=expires_in,
            )
            return url
        except ClientError as exc:
            logger.error("Failed to generate presigned URL: %s", exc)
            raise

    async def delete_file(self, storage_key: str) -> bool:
        """
        Delete a file from B2.

        Returns True if deleted successfully, False otherwise.
        """
        try:
            self._client.delete_object(
                Bucket=self._bucket,
                Key=storage_key,
            )
            logger.info("Deleted file from B2: key=%s", storage_key)
            return True
        except ClientError as exc:
            logger.error("Failed to delete file from B2: %s", exc)
            return False


def get_storage_service() -> StorageService:
    """Factory function for StorageService."""
    return StorageService()
