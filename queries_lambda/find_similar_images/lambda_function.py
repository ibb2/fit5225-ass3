import base64
import boto3
import json
import src.object_detection as object_detection
from boto3.dynamodb.conditions import Key, Attr
from requests_toolbelt.multipart import decoder


aws_region = 'us-east-1'
boto3.setup_default_session(region_name=aws_region)

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('user_detected_objects')


# def lambda_handler(event, context):

#     detected_objects = object_detection.run(event['body'])

#     # Perform the scan operation with the filter expression
#     filter_expression = Attr('tags').contains(detected_objects)
#     response = table.scan(FilterExpression=filter_expression)

#     # while 'LastEvaluatedKey' in response:
#     #     response = table.scan(FilterExpression=filter_expression,
#     #                           ExclusiveStartKey=response['LastEvaluatedKey'])
#     #     items.extend(response['Items'])

#     matched_images = []
#     for entity in response['Items']:
#         # Assuming thumbnail URLs follow a specific pattern
#         thumbnail_url = entity['tb_src_s3']
#         matched_images.append(thumbnail_url)

#     return {
#         "isBase64Encoded": True,
#         "statusCode": 200,
#         "headers": {"Content-Type": "application/json"},
#         "body": json.dumps(event['body'])
#     }

def lambda_handler(event, context):
    try:
        # # Decode the base64-encoded body
        # decoded_body = base64.b64decode(event['body'])

        # # Parse the multipart form data
        # content_type = event['headers'].get('Content-Type') or event['headers'].get('content-type')
        # multipart_data = decoder.MultipartDecoder(decoded_body, content_type)

        # # Extract the file from the multipart data
        # file_content = None
        # for part in multipart_data.parts:
        #     content_disposition = part.headers[b'Content-Disposition'].decode()
        #     if 'filename' in content_disposition:
        #         file_content = part.content
        #         break

        # if file_content is None:
        #     raise ValueError("File not found in the request")

        # Now file_content holds the binary data of the uploaded file
        # You can process the file as needed, e.g., save to S3, analyze, etc.

        return {
            "isBase64Encoded": False,
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"message": "File processed successfully"})
        }

    except Exception as e:
        return {
            "isBase64Encoded": False,
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": str(e)})
        }
