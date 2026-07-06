"""Compatibility package exposing the async AWS client wrappers."""

from __future__ import annotations

from shared.aws_clients.base import BaseAWSClient
from shared.aws_clients.exceptions import AWSClientError
from shared.aws_clients.s3 import S3Client
from shared.aws_clients.sqs import SQSClient
from shared.aws_clients.secrets_manager import SecretsManagerClient

__all__ = [
    "AWSClientError",
    "BaseAWSClient",
    "S3Client",
    "SQSClient",
    "SecretsManagerClient",
]
