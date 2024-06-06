import json  

import boto3
import os

s3_client = boto3.client('s3')

def lambda_handler(event, context):
    image_id = event['queryStringParameters']['imageId']
    bucket_name = 'your-bucket-name'
    s3_key = f'images/{image_id}.jpg'

    try:
        response = s3_client.delete_object(Bucket=bucket_name, Key=s3_key)
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Image deleted successfully'}),  
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            }
        }
    except Exception as e:
        print(f"Error deleting image {image_id}: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Failed to delete image'}),  
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            }
        }
