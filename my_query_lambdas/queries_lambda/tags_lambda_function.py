import boto3
import json

aws_region = 'us-east-1'
boto3.setup_default_session(region_name=aws_region)

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('user_detected_objects')


def lambda_handler(event, context):
    # Extract tags from queryStringParameters
    tags = []
    for key in event.get("queryStringParameters", {}).keys():
        if key.startswith("tag"):
            tags.append(event["queryStringParameters"][key])

    # Query DynamoDB for images with all specified tags
    response = table.scan(
        FilterExpression=build_filter_expression(tags),
        ExpressionAttributeValues={
            f':tag{i}': tag for i, tag in enumerate(tags)
        }
    )

    # Extract URLs of matching images
    image_urls = [item['src_s3'] for item in response['Items']]

    return {
        "isBase64Encoded": True,
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({'links': image_urls})
    }


def build_filter_expression(tags):
    filters = []
    for i in range(len(tags)):
        filters.append(f'contains(tags, :tag{i})')
    return ' and '.join(filters)
