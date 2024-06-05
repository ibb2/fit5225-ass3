import boto3
import json

aws_region = 'us-east-1'
boto3.setup_default_session(region_name=aws_region)

s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('PixTagImagesTable')

def lambda_handler(event, context):
    request_body = json.loads(event['body'])
    urls = request_body['urls']

    for url in urls:
        # Delete image from S3
        bucket_name, key = extract_bucket_key(url)
        s3.delete_object(Bucket=bucket_name, Key=key)

        # Delete entry from DynamoDB
        table.delete_item(Key={'OriginalImage': url})

    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'Images deleted successfully'}),
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        }
    }

def extract_bucket_key(url):
    parts = url.replace('s3://', '').split('/')
    bucket_name = parts[0]
    key = '/'.join(parts[1:])
    return bucket_name, key



