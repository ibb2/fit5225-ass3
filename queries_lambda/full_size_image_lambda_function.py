import boto3
import json

aws_region = 'us-east-1'
boto3.setup_default_session(region_name=aws_region)

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('PixTagImagesTable')

def lambda_handler(event, context):
    thumbnail_urls = json.loads(event['body'])['thumbnail_urls']

    # Query DynamoDB for full-size image URLs based on thumbnail URLs
    response = []
    for url in thumbnail_urls:
        result = table.get_item(Key={'ThumbnailImage': url})
        if 'Item' in result:
            response.append(result['Item']['OriginalImage'])

    return {
        'statusCode': 200,
        'body': json.dumps({'links': response}),
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        }
    }
