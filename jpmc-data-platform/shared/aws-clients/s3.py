"""Compatibility wrapper exposing the shared S3 client."""

from __future__ import annotations

from shared.aws_clients.s3 import S3Client

__all__ = ["S3Client"]
