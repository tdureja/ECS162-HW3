from flask import Flask, jsonify, request, session, send_from_directory, redirect
import os
import requests
from flask_cors import CORS
from authlib.integrations.flask_client import OAuth
from authlib.common.security import generate_token

# Initialize Flask app
app = Flask(__name__, static_folder=os.getenv('STATIC_PATH', 'static'), template_folder=os.getenv('TEMPLATE_PATH', 'templates'))
CORS(app)
app.secret_key = os.urandom(24)

# OAuth Setup (Dex authentication)
oauth = OAuth(app)
nonce = generate_token()

# Register OAuth client correctly
oauth.register(
    name='dex',
    client_id=os.getenv('OIDC_CLIENT_ID'),
    client_secret=os.getenv('OIDC_CLIENT_SECRET'),
    server_metadata_url="http://localhost:5556/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"}
)

# API Key Route
@app.route('/api/key')
def get_key():
    return jsonify({'apiKey': os.getenv('NYT_API_KEY')})

# Fetch articles from NYT
@app.route('/api/articles')
def get_articles():
    try:
        nyt_api_key = os.getenv('NYT_API_KEY')
        search_terms = ["Davis, California", "UC Davis", "Sacramento", "Yolo County", "West Sacramento", "Woodland"]
        articles = []
        for term in search_terms:
            url = f'https://api.nytimes.com/svc/search/v2/articlesearch.json?q={term}&begin_date=20230101&sort=newest&api-key={nyt_api_key}'
            response = requests.get(url)
            data = response.json()
            print(data)
            if data.get('response') and 'docs' in data['response']:
                articles.extend(data['response']['docs'])
        articles = list({article['_id']: article for article in articles}.values())
        return jsonify({'articles': articles})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Comment handling
comments = []

@app.route('/api/comments', methods=['POST'])
def post_comment():
    data = request.get_json()
    comments.append(data)
    return jsonify({"status": "success"})

@app.route('/api/comments', methods=['GET'])
def get_comments():
    return jsonify(comments)

# Authentication routes
@app.route('/')
def home():
    user = session.get('user')
    if user:
        return f"<h2>Logged in as {user['email']}</h2><a href='/logout'>Logout</a>"
    return '<a href="/login">Login with Dex</a>'

@app.route('/login')
def login():
    session['nonce'] = nonce
    redirect_uri = 'http://localhost:8000/authorize'
    return oauth.dex.authorize_redirect(redirect_uri, nonce=nonce)

@app.route('/authorize')
def authorize():
    token = oauth.dex.authorize_access_token()
    user_info = oauth.dex.parse_id_token(token, nonce=session.get('nonce'))
    session['user'] = user_info
    return redirect('/')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# Serve static frontend
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    static_path = os.getenv('STATIC_PATH', 'static')
    template_path = os.getenv('TEMPLATE_PATH', 'templates')
    if path != '' and os.path.exists(os.path.join(static_path, path)):
        return send_from_directory(static_path, path)
    return send_from_directory(template_path, 'index.html')

if __name__ == '__main__':
    debug_mode = os.getenv('FLASK_ENV') != 'production'
    app.run(debug=debug_mode, host='0.0.0.0', port=int(os.environ.get('PORT', 8000)))
