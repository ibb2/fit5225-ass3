import json
from flask import Flask, render_template, request, redirect, url_for, session
import boto3
from botocore.exceptions import NoCredentialsError

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Load configuration
with open('config.json') as config_file:
    config = json.load(config_file)

S3_BUCKET = config['src_bucket']
DST_BUCKET = config['dst_bucket']
S3_REGION = config['region']
COGNITO_REGION = config['cognito_region']
COGNITO_POOL_ID = config['cognito_pool_id']
COGNITO_CLIENT_ID = config['cognito_client_id']

# Initialize AWS clients
s3_client = boto3.client('s3', region_name=S3_REGION)
cognito_client = boto3.client('cognito-idp', region_name=COGNITO_REGION)

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
                s3_client.upload_fileobj(file, S3_BUCKET, file.filename)
                return 'File uploaded successfully!'
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
