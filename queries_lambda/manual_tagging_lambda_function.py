import boto3
import json
from decimal import *

aws_region = 'us-east-1'
boto3.setup_default_session(region_name=aws_region)

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('user_detected_objects')


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

    index = 0
    for url in urls:
        try:
            response = table.scan(
                FilterExpression='src_s3 = :val',
                ExpressionAttributeValues={
                    ':val': url.replace("%40", "@")
                }
            )

            if operation_type == 1:  # Add tags
                for item in response["Items"]:
                    item["tags"][tags[index]] = Decimal(1)
                    updated_item = table.update_item(
                        Key={'id': item['id']},
                        UpdateExpression='SET tags = :tags',
                        ExpressionAttributeValues={':tags': item['tags']}
                    )

            elif operation_type == 0:  # Remove tags
                print("Tags output")
                print(response["Items"])
                for item in response["Items"]:
                    print(item)
                    del item["tags"][tags[index]]
                    print(item)
                    updated_item = table.update_item(
                        Key={'id': item['id']},
                        UpdateExpression='SET tags = :tags',
                        ExpressionAttributeValues={':tags': item['tags']}
                    )
                    print(updated_item)
                updated_tags = [tag for tag in current_tags if tag not in tags]

        except dynamodb.meta.client.exceptions.ResourceNotFoundException as e:
            return {
                "isBase64Encoded": False,
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({'message': f'Item not found for imageId: {url}'})
            }
        except Exception as e:
            return {
                "isBase64Encoded": False,
                "statusCode": 500,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({'message':  str(e)})
            }
        index += 1

    return {
        "isBase64Encoded": False,
        "statusCode": 500,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({'message':  'Tags updated successfully'})
    }
