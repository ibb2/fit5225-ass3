import json
import base64
import os
import boto3
from botocore.exceptions import ClientError
import src.object_detection as object_detection

dynamodb = boto3.resource('dynamodb')
user_table = dynamodb.Table('user_detected_objects')


def lambda_handler(event, context):
    # Initialize logging
    import logging
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Extract base64 image data from event
    try:
        print(event['image'].encode('utf-8'))
        image_data = event['image'].encode('utf-8')
        print(f"Image Data: {image_data}")
        logger.info("Received image data")
    except KeyError as e:
        logger.error("Missing image data in the request")

        return {
            "isBase64Encoded": False,
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({'message': "Missing image data in the request"})
        }

    # Decode base64 image
    try:
        decoded_image = base64.b64decode(image_data)
        print(f"Decoded Images: {decoded_image}")
        detected_objects = object_detection(decoded_image)
        logger.info("Image data successfully decoded")
    except Exception as e:
        logger.error(f"Failed to decode image data: {str(e)}")

        return {
            "isBase64Encoded": False,
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({'message': "Failed to decode image data"})
        }

    # Further processing and interactions with DynamoDB
    try:

        response = user_table.scan()  # All the items

        s3_urls = []

        for detected_object in detected_objects:

            for item in response["Items"]:
                for key, value in item.items():
                    if key == "tags":
                        if detected_object in value:
                            s3_urls.append(item["s3_url"])
                            print("Here")

    except ClientError as e:
        logger.error(f"DynamoDB client error: {str(e)}")

        return {
            "isBase64Encoded": False,
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({'message': "DynamoDB client error"})
        }
    except Exception as e:
        logger.error(f"Failed to process image: {str(e)}")

        return {
            "isBase64Encoded": False,
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({'message': "Failed to process image"})
        }

    # Successful response
    return {
        "isBase64Encoded": False,
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({'message': "Image processed successfully"})
    }
