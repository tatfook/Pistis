from flask import session, redirect, url_for, escape, request
from flask import render_template, json, jsonify
from pistis import app
import os

# set the secret key.  keep this really secret:
app.secret_key = b',\x90\xebYS\xd1\xfa(%\x91s\xf3\x9a\xb9^\xe1x\xf5\xb3\xac\x98\xf7i\xaf\x18V'

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
#       ${field}/                    only keepwork
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
    manifest = request.get_json(silent=True)
    if manifest is None:
        return jsonify(error='manifest not exists')

    if 'field' not in manifest:
        return jsonify(
            error='key "field" not exists'
        )
    if manifest['field'] not in ['keepwork']:
        return jsonify(
            error='unsupported field {field}'.format(field=manifest['field'])
        )
    if manifest['field'] == 'keepwork' and (not all (k in manifest for k in ("field", "author", "work", "identity"))):
        return jsonify(
            error='incomplete manifest for field keepwork'
        )

    # write file
    store_root = app.config['STORE_ROOT']
    store_path = '{root}/v1/manifests/{field}/{author}/{work}/manifest.json'.format(
        root=store_root,
        field=manifest['field'],
        author=manifest['author'],
        work=manifest['work'],
    )
    store_dir = os.path.dirname(store_path)
    if not os.path.isdir(store_dir):
        os.makedirs(store_dir)

    with open(store_path, 'w') as f:
        f.write(json.dumps(manifest))

    return jsonify(manifest)


# GET /api/v1/manifest
#
# param
# - url: keepwork.com/dukes/test-report
#
# extract
# - field=
# - author=
# - work=
# from url
@app.route('/api/v1/manifest', methods=['GET'])
def search_manifest():
    pass




@app.route('/page/v1/manifest', methods=['GET'])
def search_manifest_page():
    pass

