from flask import redirect, url_for, escape, request
from flask import render_template, json, jsonify
from pistis import app, git
from urllib.parse import urlparse

from pistis.apis import search_manifest

@app.route('/')
def index():
    return redirect(url_for('search_manifest_page'))

@app.route('/page/v1/search', methods=['GET'])
def search_manifest_page():
    query = request.args
    if 'url' not in query:
        return render_template('search.html')

    # http://keepwork.com/dukes/paracraft
    url = query['url']

    p = urlparse(url.strip('/'))
    host = p.hostname      # keepwork.com
    path = p.path          # /dukes/paracraft

    field_map = {
        'keepwork.com': 'keepwork'
    }
    field = field_map[host]

    (author, work) = path.strip('/').split('/')

    return render_template(
        'manifest.html',
        author=author,
        work=work,
        data=search_manifest(field, author, work)
    )

