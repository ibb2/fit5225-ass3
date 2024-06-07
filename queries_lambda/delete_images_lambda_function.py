import json

import boto3
import os

s3_client = boto3.client('s3')

boto3.setup_default_session(region_name="us-east-1")

dynamodb = boto3.resource('dynamodb')
user_table = dynamodb.Table('user_detected_objects')


def lambda_handler(event, context):
    "https://fit5225-ass3-group101-24-thumbnails.s3.amazonaws.com/thumbnails-ibyster824%40gmail.com/000000012807.jpg"
    email = event['queryStringParameters']['email']
    url = event['queryStringParameters']['thumbnail']

    thumbnail_name = url.split('/', 3)[-1].replace("%40", "@")
    print(thumbnail_name)

    # image_id = event['queryStringParameters']['imageId']
    src_bucket_name = 'fit5225-ass3-group101-24'
    tb_src_bucket_name = "fit5225-ass3-group101-24-thumbnails"
    s3_key = f'{thumbnail_name}'
    tb_s3_key = f'thumbnails-{thumbnail_name}'
    print("line break")
    print(s3_key)
    print(tb_s3_key)

    try:
        src_bucket_response = s3_client.delete_object(
            Bucket=src_bucket_name, Key=s3_key)
        tb_bucket_response = s3_client.delete_object(
            Bucket=tb_src_bucket_name, Key=tb_s3_key)

        print(src_bucket_response)
        print(tb_bucket_response)

        thumbnail = url.replace("%40", "@")

        response = user_table.scan(
            FilterExpression='tb_src_s3 = :val',
            ExpressionAttributeValues={
                ':val': thumbnail
            }
        )

        for item in response['Items']:
            # Extract the id of the item
            item_id = item['id']

            # Delete the item from DynamoDB using the id
            user_table.delete_item(
                Key={
                    'id': item_id
                }
            )

        return {
            "isBase64Encoded": False,
            "statusCode": 300,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({'message': "Successfully deleted item"})
        }
    except Exception as e:
        print(f"Error deleting image {image_id}: {str(e)}")
        return {
            "isBase64Encoded": False,
            "statusCode": 300,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({'message': e})
        }
