# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core import patch_all

# Patch all AWS SDK calls for X-Ray tracing
patch_all()

import boto3
import os
import json
import logging
import uuid

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb_client = boto3.client("dynamodb")


@xray_recorder.capture('handler')
def handler(event, context):
    table = os.environ.get("TABLE_NAME")
    
    # Add X-Ray annotations for filtering and analysis
    xray_recorder.put_annotation('table_name', table)
    xray_recorder.put_annotation('function_name', context.function_name)
    
    logging.info(f"## Loaded table name from environemt variable DDB_TABLE: {table}")
    if event["body"]:
        item = json.loads(event["body"])
        logging.info(f"## Received payload: {item}")
        year = str(item["year"])
        title = str(item["title"])
        id = str(item["id"])
        
        # Add metadata for additional context
        xray_recorder.put_metadata('item_id', id)
        xray_recorder.put_metadata('item_year', year)
        
        dynamodb_client.put_item(
            TableName=table,
            Item={"year": {"N": year}, "title": {"S": title}, "id": {"S": id}},
        )
        message = "Successfully inserted data!"
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"message": message}),
        }
    else:
        logging.info("## Received request without a payload")
        default_id = str(uuid.uuid4())
        
        # Add metadata for default item
        xray_recorder.put_metadata('item_id', default_id)
        xray_recorder.put_metadata('default_item', True)
        
        dynamodb_client.put_item(
            TableName=table,
            Item={
                "year": {"N": "2012"},
                "title": {"S": "The Amazing Spider-Man 2"},
                "id": {"S": default_id},
            },
        )
        message = "Successfully inserted data!"
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"message": message}),
        }
