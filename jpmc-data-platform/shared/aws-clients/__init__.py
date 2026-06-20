"""AWS client wrappers for the JPMC data platform."""

from .base import BaseAWSClient
from .exceptions import AWSClientError
from .cloudwatch_logs import CloudWatchLogsClient
from .dynamodb import DynamoDBClient
from .glue import GlueClient
from .lake_formation import LakeFormationClient
from .s3 import S3Client
from .secrets_manager import SecretsManagerClient
from .sqs import SQSClient

__all__ = [
    "AWSClientError",
    "BaseAWSClient",
    "GlueClient",
    "S3Client",
    "CloudWatchLogsClient",
    "SecretsManagerClient",
    "LakeFormationClient",
    "DynamoDBClient",
    "SQSClient",
]
