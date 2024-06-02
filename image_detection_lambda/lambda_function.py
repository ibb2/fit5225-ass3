import json
import boto3
from io import StringIO
import pandas as pd
from object_detection import run

s3_client = boto3.client('s3')

def lambda_handler(event, context):

    src_bucket = event["Records"][0]["s3"]["bucket"]["name"]
    src_bucket_key = event["Records"][0]["s3"]["object"]["key"]
    dst_bucket =  + f"{src_bucket}-identified-tags"
    dst_key = f"identified-tags-{src_bucket_key}"

    try:        
        selected_bucket = s3_client.get_object(Bucket=src_bucket, Key=src_bucket_key)
        body = selected_bucket['Body']
        decoded_image = body.read().decode('utf-8')
        response = run(decoded_image)

        detected_object = {
            'id': event['Records'][0]['s3']['object']['key'],
            's3': dst_key,
            'tags': json.dumps(response)
        }

        print(detected_object)
        
        s3_client.put_object(Body=json.dumps(detected_object),Bucket=dst_bucket, Key=dst_key)
        
    except Exception as err:
        print(err)
        
    return {
        'statusCode': 200,
        'id': event['Records'][0]['s3']['object']['key'],
        's3': dst_key,
        'tags': json.dumps(response)
    }
