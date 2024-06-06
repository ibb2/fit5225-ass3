import json


def lambda_handler(event, context):
    thumbnail_urls = json.loads(event['body'])['thumbnail_urls']

    src_url = thumbnail_urls.slice(10)
    data = {
        "src_url": src_url
    }

    return {
        "isBase64Encoded": True,
        "statusCode": 200,
        "headers": {'Content-Type': 'application/json'},
        "body": json.dumps(data)
    }
