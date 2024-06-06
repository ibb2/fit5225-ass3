import boto3
import json

aws_region = 'us-east-1'
boto3.setup_default_session(region_name=aws_region)

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('PixTagImagesTable')

def lambda_handler(event, context):
    try:
        request_body = json.loads(event['body'])
        urls = request_body['urls']
        tags = request_body['tags']
        operation_type = request_body['type']
    except KeyError as e:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': f'Missing key: {str(e)}'}),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            }
        }
    except json.JSONDecodeError:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Invalid JSON format'}),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            }
        }

    for url in urls:
        try:
            item = table.get_item(Key={'imageId': url})
            current_tags = item.get('Item', {}).get('Tags', [])

            if operation_type == 1:  # Add tags
                updated_tags = list(set(current_tags + tags))
            elif operation_type == 0:  # Remove tags
                updated_tags = [tag for tag in current_tags if tag not in tags]

            # Update DynamoDB item with new tags
            table.update_item(
                Key={'imageId': url},
                UpdateExpression='SET Tags = :tags',
                ExpressionAttributeValues={':tags': updated_tags}
            )
        except dynamodb.meta.client.exceptions.ResourceNotFoundException as e:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': f'Item not found for imageId: {url}'}),
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                }
            }
        except Exception as e:
            return {
                'statusCode': 500,
                'body': json.dumps({'error': str(e)}),
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                }
            }

    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'Tags updated successfully'}),
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        }
    }
