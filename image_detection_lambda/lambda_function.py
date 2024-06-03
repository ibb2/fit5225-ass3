import json
import os
import boto3
import src.object_detection as object_detection
from uuid import uuid4

s3_client = boto3.client('s3')


def lambda_handler(event, context):

    src_bucket = event["detail"]["bucket"]["name"]
    src_bucket_key = event["detail"]["object"]["key"]
    dst_bucket = f"{src_bucket}-identified-tags"
    dst_key = f"identified-tags-{src_bucket_key}"

    try:

        file_extension = os.path.splitext(src_bucket_key)[1]
        if (file_extension != ".jpg" and file_extension != ".jpeg" and file_extension != ".png"):
            return {
                'statusCode': 400,
                'message': 'Only jpg/jpeg/png files are allowed'
            }
        else:
            print("FIle type permitted")

        response = s3_client.get_object(Bucket=src_bucket, Key=src_bucket_key)
        file_stream = response['Body'].read()
        try:
            s3_client.download_file(
                src_bucket, 'yolov3-tiny.weights', '/tmp/yolov3-tiny.weights')
        except Exception as err:
            print(err)

        try:
            detected_object = object_detection.run(file_stream)

            dst_name = os.path.splitext(dst_key)[0]
            detected_object_dict = {
                'id': str(uuid4()),
                'src_s3': f"https://fit5225-ass3-group101-24.s3.amazonaws.com/{src_bucket_key}",
                'dst_s3': f"https://fit5225-ass3-group101-24-identified-tags.s3.amazonaws.com/{dst_name}",
                'tags': detected_object
            }

            s3_client.put_object(Body=json.dumps(
                detected_object_dict), Bucket=dst_bucket, Key=dst_name, ContentType='application/json; charset=utf-8')

            return {
                'statusCode': 200,
                'tags': detected_object
            }

        except Exception as err:
            return {
                'statusCode': 300,
                'error': str(err)
            }

    except Exception as err:
        return {
            'statusCode': 500,
            'error': str(err)
        }
