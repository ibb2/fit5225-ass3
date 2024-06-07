import base64
import json
import logging
import os
import boto3
import requests

from flask import Flask, render_template, request, redirect, url_for, session, flash

from botocore.exceptions import NoCredentialsError
from requests_aws4auth import AWS4Auth

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Load configuration
with open('config.json') as config_file:
    config = json.load(config_file)

S3_BUCKET = config['src_bucket']
DST_BUCKET = config['dst_bucket']
S3_REGION = config['region']
COGNITO_POOL_ID = config['cognito_pool_id']
COGNITO_CLIENT_ID = config['cognito_client_id']
QUERY_API = config['api_key']
SNS_TOPIC_ARN = config['sns_topic_arn']

# Initialize AWS clients
s3_client = boto3.client('s3', region_name=S3_REGION)
cognito_client = boto3.client('cognito-idp', region_name=S3_REGION)
sns_client = boto3.client('sns', region_name=S3_REGION)


@app.route('/')
def home():

    if 'username' not in session:
        loggedIn = False
    else:
        loggedIn = True

    return render_template('home.html', data={"loggedIn": loggedIn})


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        password = request.form['password']

        try:
            response = cognito_client.sign_up(
                ClientId=COGNITO_CLIENT_ID,
                Username=email,
                Password=password,
                UserAttributes=[
                    {'Name': 'email', 'Value': email},
                    {'Name': 'given_name', 'Value': first_name},
                    {'Name': 'family_name', 'Value': last_name}
                ]
            )
            return redirect(url_for('login'))
        except Exception as e:
            return str(e)
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        try:
            response = cognito_client.initiate_auth(
                ClientId=COGNITO_CLIENT_ID,
                AuthFlow='USER_PASSWORD_AUTH',
                AuthParameters={
                    'USERNAME': email,
                    'PASSWORD': password
                }
            )

            print(response)

            session['username'] = email
            session['id_token'] = response['AuthenticationResult']['IdToken']
            return redirect(url_for('upload'))
        except Exception as e:
            return str(e)
    return render_template('login.html')


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        file = request.files['file']
        if file:
            try:
                filename, extension = os.path.splitext(file.filename)

                if extension in ['.jpg', '.jpeg', '.png']:

                    response = s3_client.generate_presigned_post(
                        S3_BUCKET,
                        f"{session['username']}/{file.filename}",
                        Fields=None,
                        Conditions=None,
                        ExpiresIn=3600
                    )

                    logging.error(response)
                    files = {'file': (filename, file)}

                    http_response = requests.post(
                        url=response['url'], data=response['fields'], files=files)

                    # Successful status codes (2xx)
                    if http_response.status_code in range(200, 299):
                        print(f'File upload HTTP status code: {
                              http_response.status_code}')
                        return 'File uploaded successfully!'
                    else:
                        # Handle other status codes (4xx, 5xx)
                        error_message = f'File upload failed with status code {
                            http_response.status_code}'
                        if http_response.text:
                            error_message += f'\nResponse: {
                                http_response.text}'
                        return error_message
                else:
                    return 'Invalid file type'

            except NoCredentialsError:
                return 'Credentials not available'
    return render_template('upload.html')


@app.route('/settings', methods=['GET', 'POST'])
def settings():

    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':

        tags = request.form['subscribe'].split(', ')

        subscribe_url = "https://paopwei6pc.execute-api.us-east-1.amazonaws.com/fit5225-ass3-production/subscribe"

        headers = {
            'Authorization': f'Bearer {session['id_token']}'
        }

        params = {
            "username": session['username'],
        }

        for i in range(len(tags)):
            params[f'tag{i+1}'] = tags[i]

        print(params)

        response = requests.get(subscribe_url, headers=headers, params=params)
        print(response.json())

        if response.status_code == 200:
            flash('Subscription request sent. Please check your email to confirm.')
        else:
            flash("Failed to send subscription request.")

    return render_template('settings.html')


@app.route('/query', methods=['GET'])
def query():
    if 'username' not in session:
        return redirect(url_for('login'))

    return render_template('query.html')


@app.route('/query/search/tags', methods=['GET', 'POST'])
def query_by_tags():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        tags = request.form['tags'].split(',')
        print(tags)

        credentials = boto3.Session().get_credentials()
        auth = AWS4Auth(credentials.access_key, credentials.secret_key,
                        S3_REGION, 'execute-api', session_token=credentials.token)

        params = {}

        for i in range(len(tags)):
            params[f'tag{i+1}'] = tags[i]

        headers = {
            'Authorization': f'Bearer {session['id_token']}'
        }

        get_tags_url = "https://paopwei6pc.execute-api.us-east-1.amazonaws.com/fit5225-ass3-production/search"

        response = requests.get(
            get_tags_url, headers=headers, params=params)

        data = response.json()['links']
        unique_url = set(data)
        print(data)

        return render_template('/query/search/tags.html', data=unique_url)
    return render_template('/query/search/tags.html')


@app.route('/query/search/full-image', methods=['GET', 'POST'])
def query_by_thumbnail():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        thumbnail_url = request.form['thumbnail-url'].split(',')

        # credentials = boto3.Session().get_credentials()
        # auth = AWS4Auth(credentials.access_key, credentials.secret_key,
        #                 S3_REGION, 'execute-api', session_token=credentials.token)

        params = {
            "thumbnail_url": thumbnail_url[0]
        }

        headers = {
            'Authorization': f'Bearer {session['id_token']}'
        }

        get_tags_url = "https://paopwei6pc.execute-api.us-east-1.amazonaws.com/fit5225-ass3-production/search/thumbnails"

        response = requests.get(
            get_tags_url, headers=headers, params=params)

        print(response.json())
        print("---------------------------")
        data = response.json()["src_url"]

        return render_template('/query/search/thumbnails.html', data=data)
    return render_template('/query/search/thumbnails.html')


@app.route('/query/search/image', methods=['GET', 'POST'])
def query_by_image():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        uploaded_file = request.files['file']

        if uploaded_file.filename != '' and (uploaded_file.filename[-4:] == '.jpg' or uploaded_file.filename[-5:] == '.jpeg' or uploaded_file.filename[-4:] == '.png'):

            image = {'image': base64.b64encode(
                uploaded_file.read()).decode('utf-8')}

            file = base64.b64encode(uploaded_file.read()).decode('utf-8')

            headers = {
                'Authorization': f'Bearer {session['id_token']}',
            }

            file_content = base64.b64encode(
                uploaded_file.read()).decode('utf-8')
            payload = json.dumps({
                'isBase64Encoded': True,
                'file': file_content,
                'filename': uploaded_file.filename
            })

            similar_images_url = "https://paopwei6pc.execute-api.us-east-1.amazonaws.com/fit5225-ass3-production/search/images"

            # response = requests.post(
            #     similar_images_url, data=image, headers=headers)
            response = requests.post(
                similar_images_url, data=payload, headers=headers)

            print(response.json())
            print("---------------------------")

            # data = response.json()["similar_images_urls"]

            return render_template('/query/search/images.html', data={})

    if request.method == 'GET':
        return render_template('/query/search/images.html')


@ app.route('/query/edit/manual-edit', methods=['GET', 'POST'])
def query_edit_data():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == "POST":
        edit_url = "https://paopwei6pc.execute-api.us-east-1.amazonaws.com/fit5225-ass3-production/manual-tagging"

        urls = request.form['urls'].split(',')
        type = request.form['type']
        tags = request.form['tags'].split(',')

        headers = {
            'Authorization': f'Bearer {session['id_token']}',
        }

        data = {
            'urls': urls,
            'type': int(type),
            'tags': tags
        }

        response = requests.post(
            edit_url, headers=headers, data=json.dumps(data))

        print(response.json())

    return render_template('/query/edit/manual-edit.html', data={})


@ app.route('/query/images/delete', methods=['GET', 'POST', 'DELETE'])
def query_delete_data():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == "DELETE" or request.method == 'POST':

        delete_url = "https://paopwei6pc.execute-api.us-east-1.amazonaws.com/fit5225-ass3-production/delete/image"
        thumbnail = request.form['delete']
        email = session['username']

        headers = {
            'Authorization': f'Bearer {session['id_token']}',
        }

        response = requests.delete(
            delete_url, params={'email': email, 'thumbnail': thumbnail}, headers=headers)
        print(response.json())
        return render_template('/query/images/delete.html')

    if request.method == 'GET':
        return render_template('/query/images/delete.html')


@ app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
