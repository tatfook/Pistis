from flask import session, redirect, url_for, escape, request
from flask import render_template
from pistis import app
import json, os

# set the secret key.  keep this really secret:
app.secret_key = b',\x90\xebYS\xd1\xfa(%\x91s\xf3\x9a\xb9^\xe1x\xf5\xb3\xac\x98\xf7i\xaf\x18V'
app.config['STORE_ROOT'] = 'store'

@app.route('/')
def index():
    return render_template('index.html')


# POST /api/v1/manifest
#
# {
#   "field": "keepwork",
#   "author": "${author_name}",
#   "work": "${work_name}",
#   "identity": "${commit_hash}"
# }
#
# error
# {
#   "error": "${error_msg}"
# }
#
# success
# {
#   "field": "keepwork",
#   "author": "${author_name}",
#   "work": "${work_name}",
#   "identity": "${commit_hash}"
# }
#
#
# store manifest as a normal file
#
# store.git/
#   v1/
#     manifests/
#       ${field}/
#         ${author}/
#           ${work}/
#             manifest.json
#     blockchains/
#       ${service}/   ethereum or bitcoin
#         ${store.git commit hash}/
#           record.json
#
@app.route('/api/v1/manifest', methods=['POST'])
def add_manifest():
    # parse json data
    manifest = request.get_json(silent=True)
    if manifest is None:
        return json.dumps(
            dict(error='parse json failed')
        )
    # check json keys
    if not all (k in manifest for k in ("field", "author", "work", "identity")):
        return json.dumps(
            dict(error='manifest is not invalid')
            )
    # write file
    store_root = app.config['STORE_ROOT']
    return json.dumps(manifest)


# GET /api/v1/manifest
#
# - must: field=
# - opt:  author=
# - opt:  work=
# - opt:  identity=
#
@app.route('/api/v1/manifest', methods=['GET'])
def search_manifest():
    pass




@app.route('/page/v1/manifest', methods=['GET'])
def search_manifest_page():
    pass


