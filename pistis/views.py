from flask import redirect, url_for, escape, request
from flask import render_template, json, jsonify
from pistis import app, git

@app.route('/')
def index():
    return redirect(url_for('search_manifest_page'))

@app.route('/page/v1/search', methods=['GET'])
def search_manifest_page():
    return render_template('search.html')

@app.route('/page/v1/manifest', methods=['GET'])
def list_manifest_page():
    return render_template('manifest.html')
