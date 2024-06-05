import boto3
import json

aws_region = 'us-east-1'
boto3.setup_default_session(region_name=aws_region)

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('PixTagImagesTable')

def lambda_handler(event, context):
    request_body = json.loads(event['body'])
    urls = request_body['urls']
    tags = request_body['tags']
    operation_type = request_body['type']

    for url in urls:
        item = table.get_item(Key={'OriginalImage': url})
        if 'Item' in item:
            current_tags = item['Item'].get('Tags', [])

            if operation_type == 1:  # Add tags
                updated_tags = list(set(current_tags + tags))
            elif operation_type == 0:  # Remove tags
                updated_tags = [tag for tag in current_tags if tag not in tags]

            # Update DynamoDB item with new tags
            table.update_item(
                Key={'OriginalImage': url},
                UpdateExpression='SET Tags = :tags',
                ExpressionAttributeValues={':tags': updated_tags}
            )

    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'Tags updated successfully'}),
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        }
    }
