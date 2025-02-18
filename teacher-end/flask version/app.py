from flask import Flask, request, session, render_template, url_for
from pylti1p3.contrib.flask import FlaskOIDCLogin, FlaskMessageLaunch
from pylti1p3.tool_config import ToolConfJsonFile
import os
import json

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Configuration for your tool
config = {
    "https://k12.instructure.com": {
        "client_id": "10000000000000",  # Replace with your client ID from Canvas
        "auth_login_url": "https://k12.instructure.com/api/lti/authorize_redirect",
        "auth_token_url": "https://k12.instructure.com/login/oauth2/token",
        "key_set_url": "https://k12.instructure.com/api/lti/security/jwks",
        "private_key_file": "private.key",
        "deployment_ids": ["1:your_deployment_id"]  # Replace with your deployment ID
    }
}

# Save config to file
with open('config.json', 'w') as f:
    json.dump(config, f)

tool_conf = ToolConfJsonFile('config.json')

@app.route('/')
def home():
    """Home page"""
    return render_template('home.html')

@app.route('/init', methods=['GET', 'POST'])
def init():
    """
    Handle the OpenID Connect (OIDC) login initiation.
    This is where Canvas will first send the request.
    """
    try:
        oidc_login = FlaskOIDCLogin(request, tool_conf, session)
        target_link_uri = request.args.get('target_link_uri', url_for('launch', _external=True))
        return oidc_login.enable_check_cookies().redirect(target_link_uri)
    except Exception as e:
        print(f"OIDC Login Error: {str(e)}")
        return str(e), 400

@app.route('/launch', methods=['GET', 'POST'])
def launch():
    """
    Handle the LTI launch after successful OIDC login.
    This is where the tool actually launches.
    """
    try:
        message_launch = FlaskMessageLaunch(request, tool_conf, session)
        launch_data = message_launch.get_launch_data()
        
        # Extract useful information from launch_data
        context = {
            'user_name': launch_data.get('name', 'Unknown User'),
            'course_name': launch_data.get('context', {}).get('title', 'Unknown Course'),
            'is_instructor': message_launch.is_instructor(),
            'user_email': launch_data.get('email', 'No email provided')
        }
        
        return render_template('launch.html', **context)
    except Exception as e:
        print(f"Launch Error: {str(e)}")
        return str(e), 400

@app.route('/jwks', methods=['GET'])
def get_jwks():
    """
    Provide the public key for Canvas to verify messages
    """
    return tool_conf.get_jwks()

if __name__ == "__main__":
    # Generate private key if it doesn't exist
    if not os.path.exists('private.key'):
        os.system('openssl genpkey -algorithm RSA -out private.key -pkeyopt rsa_keygen_bits:2048')
    
    app.run(debug=True, ssl_context='adhoc', port=5000)