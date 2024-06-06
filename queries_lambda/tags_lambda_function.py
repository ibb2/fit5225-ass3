import boto3
import json

aws_region = 'us-east-1'
boto3.setup_default_session(region_name=aws_region)

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('PixTagImagesTable')

def build_filter_expression(tags):
    from boto3.dynamodb.conditions import Attr
    filter_expression = Attr('tags').contains(tags[0])
    for tag in tags[1:]:
        filter_expression = filter_expression & Attr('tags').contains(tag)
    return filter_expression

def lambda_handler(event, context):
    try:
        # Extract tags from query parameters
        tags = []
        for key in event.get("queryStringParameters", {}).keys():
            if key.startswith("tag"):
                tags.append(event["queryStringParameters"][key])
        
        if not tags:
            raise ValueError('Missing query parameter: tags')
        
        # Query DynamoDB for images with all specified tags
        response = table.scan(
            FilterExpression=build_filter_expression(tags)
        )

        # Extract URLs of matching images
        image_urls = [item['OriginalImage'] for item in response['Items']]

        return {
            "isBase64Encoded": False,
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({'image_urls': image_urls})
        }

    except KeyError as e:
        # Handle case where 'tags' are not provided in query string
        return {
            "isBase64Encoded": False,
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({'error': f"Missing query parameter: {str(e)}"})
        }
        
    except ValueError as ve:
        # Handle other errors such as empty tags list
        return {
            "isBase64Encoded": False,
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({'error': str(ve)})
        }
    
    except Exception as e:
        # Catch all other exceptions
        return {
            "isBase64Encoded": False,
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({'error': str(e)})
        }
