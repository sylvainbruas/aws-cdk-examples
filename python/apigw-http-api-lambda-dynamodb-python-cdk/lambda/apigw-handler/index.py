# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import boto3
import os
import json
import logging
import uuid

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb_client = boto3.client("dynamodb")


def handler(event, context):
    table = os.environ.get("TABLE_NAME")
    
    # Log security context with structured logging
    request_context = event.get("requestContext", {})
    identity = request_context.get("identity", {})
    
    logger.info(json.dumps({
        "event": "request_received",
        "request_id": context.request_id,
        "source_ip": identity.get("sourceIp"),
        "user_agent": identity.get("userAgent"),
        "http_method": request_context.get("httpMethod"),
        "resource_path": request_context.get("resourcePath"),
        "table_name": table,
    }))
    
    try:
        if event.get("body"):
            item = json.loads(event["body"])
            year = str(item["year"])
            title = str(item["title"])
            id = str(item["id"])
            
            # Log operation without sensitive data
            logger.info(json.dumps({
                "event": "processing_item",
                "request_id": context.request_id,
                "item_id": id,
                "operation": "put_item",
            }))
            
            dynamodb_client.put_item(
                TableName=table,
                Item={"year": {"N": year}, "title": {"S": title}, "id": {"S": id}},
            )
            
            logger.info(json.dumps({
                "event": "item_inserted",
                "request_id": context.request_id,
                "item_id": id,
                "status": "success",
            }))
            
            message = "Successfully inserted data!"
            return {
                "statusCode": 200,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"message": message}),
            }
        else:
            default_id = str(uuid.uuid4())
            
            logger.info(json.dumps({
                "event": "processing_default_item",
                "request_id": context.request_id,
                "item_id": default_id,
                "operation": "put_item",
            }))
            
            dynamodb_client.put_item(
                TableName=table,
                Item={
                    "year": {"N": "2012"},
                    "title": {"S": "The Amazing Spider-Man 2"},
                    "id": {"S": default_id},
                },
            )
            
            logger.info(json.dumps({
                "event": "default_item_inserted",
                "request_id": context.request_id,
                "item_id": default_id,
                "status": "success",
            }))
            
            message = "Successfully inserted data!"
            return {
                "statusCode": 200,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"message": message}),
            }
    except Exception as e:
        logger.error(json.dumps({
            "event": "error",
            "request_id": context.request_id,
            "error_type": type(e).__name__,
            "error_message": str(e),
        }))
        raise
