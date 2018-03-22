from flask import session, redirect, url_for, escape, request
from flask import render_template, json, jsonify
from pistis import app, git
import os
import io

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
#       ${store.git commit hash}/
#         ${service}/   ethereum or bitcoin
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
# js parse url
# - url: keepwork.com/dukes/test-report
#
# param
# - field=
# - author=
# - work=
#
# return
#   {"error": "message"}
# or
#   {"data": []}
# or
#   {
#     "data": [
#       {
#         "manifest": {
#           "field": "keepwork",
#           "author": "dukes",
#           "work": "test-report",
#           "identity": "f844aa8d4ec646c1976a0fde5257767f2387d425"
#         },
#         "pistis": {
#           "hash": "f8b18b2caa3ea7b5aadca8867a41b96c745a0257"
#         },
#         "blockchain": {
#           "ethereum": {
#             "hash": "5fa3fd4d93662491edf4c955b4e80fbc85a97d2eb30332d5b557abcad7d659a8"
#           },
#           "bitcoin": {
#             "hash": "67deccc0e3aae917d2cc12f8e4ac1aa17284f12ff01829d5b4f984f359c2e383"
#           }
#         }
#       }
#     ]
#   }
#
@app.route('/api/v1/manifest', methods=['GET'])
def search_manifest():
    query = request.args
    if 'field' not in query:
        return jsonify(error='key "field" not exists')

    field = query['field']
    if field not in ['keepwork']:
        return jsonify(error='unsupported field %s' % field)

    if field == 'keepwork' and (not all (k in query for k in ('field', 'author', 'work'))):
        return jsonify(error='incomplete query condition')

    store_root = app.config['STORE_ROOT']
    repo = git.Repo(store_root)

    path = 'v1/manifests/{field}/{author}/{work}/manifest.json'.format(
        field=field,
        author=query['author'],
        work=query['work']
    )


    output = io.StringIO()
    git.log(repo=store_root, paths=[path.encode()], outstream=output)
    commits = output.getvalue().splitlines()
    output.close()

    if len(commits) == 0:
        return jsonify(data=[])


    res_data = []
    for commit_hash in map(lambda l: l.split()[-1],
                           filter(lambda line: line.startswith('commit: '),
                                  commits)):
        output = io.StringIO()
        git.ls_tree(repo=store_root, treeish=commit_hash.encode(), outstream=output)
        trees = output.getvalue().splitlines()
        output.close()

        blob_hash = list(
            map(lambda l: l.split()[2],
                filter(lambda line: line.endswith(path), trees))
        )[0]
        blob = repo.get_object(blob_hash.encode())
        blob_content = blob.data.decode()

        blockchain_data = dict()
        for service in ['ethereum', 'bitcoin']:
            record_path = '%s/v1/blockchains/%s/%s/record.json'%(store_root, commit_hash, service)
            if os.path.exists(record_path):
                with open(record_path, 'r') as f:
                    record_content = f.read()
                blockchain_data[service] = json.loads(record_content)

        res_data.append(
            dict(
                manifest=json.loads(blob_content),
                pistis=dict(
                    hash=commit_hash
                ),
                blockchain=blockchain_data
            )
        )

    return jsonify(data=res_data)

