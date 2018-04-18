from flask import redirect, url_for, escape, request
from flask import render_template, json, jsonify
from pistis import app, git
from urllib.parse import urlparse

from pistis.apis import search_manifest
from pistis.apis import get_manifest


@app.route('/')
def index():
    return redirect(url_for('search_manifest_page'))


def parse_url(url):
    # http{,s}://keepwork.com/dukes/paracraft
    p = urlparse(url.strip('/'))
    host = p.hostname  # keepwork.com
    path = p.path  # /dukes/paracraft

    field_map = {'keepwork.com': 'keepwork'}
    field = field_map[host]

    (author, work) = path.strip('/').split('/')

    return (field, author, work)


@app.route('/page/v1/search', methods=['GET'])
def search_manifest_page():
    query = request.args
    if 'url' not in query:
        return render_template('search.html')

    if 'page' not in query:
        page = 0
    else:
        page = int(query['page'])

    url = query['url']
    page_size = 5
    (field, author, work) = parse_url(url)

    return render_template(
        'manifest.html',
        author=author,
        work=work,
        url=url,
        page=page,
        page_size=page_size,
        data=search_manifest(field, author, work, page),
    )


@app.route('/page/v1/cert', methods=['GET'])
def cert_page():
    q = request.args
    if 'url' not in q or 'pistis' not in q:
        return render_template('error.html', error='incomplete cert url')

    url = q['url']
    pistis = q['pistis']
    (field, author, work) = parse_url(url)

    return render_template(
        'cert.html', data=get_manifest(field, author, work, pistis))
