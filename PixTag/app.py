import json
import logging
import os
from flask import Flask, render_template, request, redirect, url_for, session
import boto3
from botocore.exceptions import NoCredentialsError
import requests

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

# Initialize AWS clients
s3_client = boto3.client('s3', region_name=S3_REGION)
cognito_client = boto3.client('cognito-idp', region_name=S3_REGION)

@app.route('/')
def home():
    return render_template('home.html')

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
            session['username'] = email
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

                    http_response = requests.post(url=response['url'], data=response['fields'], files=files)

                    if http_response.status_code in range(200, 299):  # Successful status codes (2xx)
                        print(f'File upload HTTP status code: {http_response.status_code}')
                        return 'File uploaded successfully!'
                    else:
                        # Handle other status codes (4xx, 5xx)
                        error_message = f'File upload failed with status code {http_response.status_code}'
                        if http_response.text:
                            error_message += f'\nResponse: {http_response.text}'
                        return error_message
                else:
                    return 'Invalid file type'

            except NoCredentialsError:
                return 'Credentials not available'
    return render_template('upload.html')

@app.route('/query', methods=['GET', 'POST'])
def query():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        tags = request.form['tags'].split(',')
        # Implement API call to query images based on tags
        # Display results
        return 'Query results here'
    return render_template('query.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
