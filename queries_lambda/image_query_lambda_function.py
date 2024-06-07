import json
import base64
import os
import boto3
from botocore.exceptions import ClientError

def lambda_handler(event, context):
    # Initialize logging
    import logging
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # Environment variable
    images_table = os.environ.get('PixTagImagesTable')
    
    if not images_table:
        logger.error("Environment variable PixTagImagesTable not set")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Environment variable PixTagImagesTable not set'})
        }
    
    # Extract base64 image data from event
    try:
        image_data = event['image']
        logger.info("Received image data")
    except KeyError as e:
        logger.error("Missing image data in the request")
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Missing image data in the request'})
        }
    
    # Decode base64 image
    try:
        decoded_image = base64.b64decode(image_data)
        logger.info("Image data successfully decoded")
    except Exception as e:
        logger.error(f"Failed to decode image data: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Failed to decode image data'})
        }
    
    # Further processing and interactions with DynamoDB
    try:
        # DynamoDB interactions (example)
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(images_table)
        
        response = table.put_item(
            Item={
                'id': 'unique-id',
                'image_data': decoded_image
            }
        )
        
        logger.info("Image data successfully stored in DynamoDB")
        
    except ClientError as e:
        logger.error(f"DynamoDB client error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'DynamoDB client error'})
        }
    except Exception as e:
        logger.error(f"Failed to process image: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Failed to process image'})
        }
    
    # Successful response
    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'Image processed successfully'})
    }
