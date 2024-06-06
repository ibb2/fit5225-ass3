import json
import logging


# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    logger.info(f"Received event: {json.dumps(event)}")

    try:
        # Extract the imageId from the query parameters
        image_id = event['queryStringParameters']['imageId']
        logger.info(f"Received imageId: {image_id}")
    except KeyError as e:
        logger.error(f"Missing query parameter: {str(e)}")
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Missing query parameter: imageId'}),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            }
        }

    # Query DynamoDB for the full-size image URL based on imageId
    try:
        result = table.get_item(Key={'imageId': image_id})
        logger.info(f"DynamoDB get_item result: {json.dumps(result)}")

        if 'Item' not in result:
            logger.warning(f"Image not found for imageId: {image_id}")
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'Image not found'}),
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                }
            }

        original_image_url = result['Item']['OriginalImage']
        logger.info(f"Found original image URL: {original_image_url}")
        return {
            'statusCode': 200,
            'body': json.dumps({'link': original_image_url}),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            }
        }
    except Exception as e:
        logger.error(f"Exception occurred: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)}),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            }
        }
