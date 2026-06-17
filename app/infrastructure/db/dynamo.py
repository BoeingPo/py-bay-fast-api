from decimal import Decimal

import boto3

from app.config import settings

_client = None


def get_dynamo_client():
    global _client
    if _client is None:
        _client = boto3.client(
            "dynamodb",
            endpoint_url=settings.dynamodb_endpoint,
            region_name=settings.aws_default_region,
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
        )
    return _client


_resource = None


def get_dynamo_resource():
    global _resource
    if _resource is None:
        _resource = boto3.resource(
            "dynamodb",
            endpoint_url=settings.dynamodb_endpoint,
            region_name=settings.aws_default_region,
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
        )
    return _resource


def get_table(name: str):
    return get_dynamo_resource().Table(name)


def serialize(item: dict) -> dict:
    result = {}
    for k, v in item.items():
        result[k] = Decimal(str(v)) if isinstance(v, float) else v
    return result


def deserialize(item: dict) -> dict:
    result = {}
    for k, v in item.items():
        if isinstance(v, Decimal):
            result[k] = int(v) if v % 1 == 0 else float(v)
        else:
            result[k] = v
    return result
