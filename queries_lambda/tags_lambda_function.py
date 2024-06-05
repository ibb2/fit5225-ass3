import boto3
import json

aws_region = 'us-east-1'
boto3.setup_default_session(region_name=aws_region)

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('PixTagImagesTable')

def lambda_handler(event, context):
    tags = event['queryStringParameters']['tags'].split(',')

    # Query DynamoDB for images with all specified tags
    response = table.scan(
        FilterExpression=build_filter_expression(tags)
    )

    # Extract URLs of matching images
    image_urls = [item['OriginalImage'] for item in response['Items']]

    return {
        'statusCode': 200,
        'body': json.dumps({'links': image_urls}),
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        }
    }

def build_filter_expression(tags):
    filters = []
    for tag in tags:
        filters.append('contains(Tags, :tag{})')
    return ' and '.join(filters)

