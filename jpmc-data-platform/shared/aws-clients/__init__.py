"""AWS client wrappers for the JPMC data platform."""

from shared.aws_clients.base import BaseAWSClient
from shared.aws_clients.exceptions import AWSClientError
from shared.aws_clients.glue import GlueClient
from shared.aws_clients.s3 import S3Client
from shared.aws_clients.secrets_manager import SecretsManagerClient
from shared.aws_clients.sqs import SQSClient

__all__ = [
    "AWSClientError",
    "BaseAWSClient",
    "GlueClient",
    "S3Client",
    "SecretsManagerClient",
    "SQSClient",
]
