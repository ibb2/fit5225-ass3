import json


def lambda_handler(event, context):
    data = event["queryStringParameters"]

    url_body = "https://fit5225-ass3-group101-24.s3.amazonaws.com/"
    tb_key_raw = data["thumbnail_url"].split('/', 3)[-1]
    tb_key = tb_key_raw.replace("%40", "@")
    src_url = url_body + tb_key[11:]

    data = {
        "src_url": src_url
    }

    return {
        "isBase64Encoded": True,
        "statusCode": 200,
        "headers": {'Content-Type': 'application/json'},
        "body": json.dumps(data)
    }
