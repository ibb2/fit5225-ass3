// app.js

// Initialize AWS SDK
AWS.config.region = 'us-east-1'; 
AWS.config.credentials = new AWS.CognitoIdentityCredentials({
    IdentityPoolId: 'us-east-1:1773050f-419e-4635-b66b-a19873531f54',
});

// Get credentials asynchronously
AWS.config.credentials.get(() => {
    // Credentials will be available here
});

// Handle sign-up form submission
document.getElementById('signup-form').addEventListener('submit', function(event) {
    event.preventDefault(); // Prevent default form submission

    // Retrieve user input
    var username = document.getElementById('username').value.trim();
    var password = document.getElementById('password').value.trim();
    var email = document.getElementById('email').value.trim();
    var name = document.getElementById('name').value.trim();

    // Configure user pool data
    var poolData = {
        UserPoolId: 'us-east-1_Ul6owkYSi', 
        ClientId: '15amp79g0ei0a2ij5ud0aalrgi' 
    };

    var userPool = new AmazonCognitoIdentity.CognitoUserPool(poolData);

    var attributeList = [];
    var dataEmail = {
        Name: 'email',
        Value: email
    };
    var dataName = {
        Name: 'name',
        Value: name
    };

    var attributeEmail = new AmazonCognitoIdentity.CognitoUserAttribute(dataEmail);
    var attributeName = new AmazonCognitoIdentity.CognitoUserAttribute(dataName);

    attributeList.push(attributeEmail);
    attributeList.push(attributeName);

    // Sign up the user
    userPool.signUp(username, password, attributeList, null, function(err, result) {
        if (err) {
            console.log('Error registering user:', err);
            document.getElementById('signup-result').innerHTML = 'Error: ' + err.message;
            return;
        }
        var cognitoUser = result.user;
        console.log('User successfully registered:', cognitoUser);
        document.getElementById('signup-result').innerHTML = 'User successfully registered!';
    });
});

// Handle sign-in form submission
document.getElementById('signin-form').addEventListener('submit', function(event) {
    event.preventDefault(); // Prevent default form submission

    // Retrieve user input
    var signinUsername = document.getElementById('signin-username').value.trim();
    var signinPassword = document.getElementById('signin-password').value.trim();

    // Configure user pool data
    var poolData = {
        UserPoolId: 'us-east-1_Ul6owkYSi', 
        ClientId: '15amp79g0ei0a2ij5ud0aalrgi' 
    };

    var userPool = new AmazonCognitoIdentity.CognitoUserPool(poolData);

    var authenticationDetails = new AmazonCognitoIdentity.AuthenticationDetails({
        Username: signinUsername,
        Password: signinPassword
    });

    var cognitoUser = new AmazonCognitoIdentity.CognitoUser({
        Username: signinUsername,
        Pool: userPool
    });

    // Sign in the user
    cognitoUser.authenticateUser(authenticationDetails, {
        onSuccess: function (result) {
            console.log('User successfully authenticated:', result);
            document.getElementById('signin-result').innerHTML = 'User successfully authenticated!';
            // Redirect or perform additional actions after successful authentication
        },
        onFailure: function (err) {
            console.log('Error authenticating user:', err);
            document.getElementById('signin-result').innerHTML = 'Error: ' + err.message;
        }
    });
});
