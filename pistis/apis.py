from flask import session, redirect, url_for, escape, request
from flask import render_template, json, jsonify
from pistis import app, git, repo

from datetime import datetime, timezone
import time
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
#         cluster/                 dirname: first 2 character of author
#           ${author}/
#             ${work}/
#               manifest.json
#     blockchains/
#       cluster/                   dirname: first 2 chars of store.git commit hash
#         ${store.git commit hash}/
#           ${service}/   ethereum or bitcoin
#             record.json
#
def cluster_name(child):
    # gather children into one cluster
    # first $cluster_param chars as cluster name
    cluster_param = 2

    if len(child) <= cluster_param:
        return child
    return child[:cluster_param]

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
    store_path = '{root}/v1/manifests/{field}/{cluster}/{author}/{work}/manifest.json'.format(
        root=store_root,
        field=manifest['field'],
        cluster=cluster_name(manifest['author']),
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
def search_manifest_api():
    query = request.args
    if 'field' not in query:
        return jsonify(error='key "field" not exists')

    field = query['field']
    if field not in ['keepwork']:
        return jsonify(error='unsupported field %s' % field)

    if field == 'keepwork' and (not all (k in query for k in ('field', 'author', 'work'))):
        return jsonify(error='incomplete query condition')

    return jsonify(
        data=search_manifest(field, query['author'], query['work'])
    )


def search_manifest(field, author, work):
    path = store_path(field, author, work)
    # %ct commit time
    commits = git.log('--pretty=format:%H', '--', path).splitlines()

    if len(commits) == 0:
        return []

    data = []
    for commit_hash in commits:
        manifest = get_manifest(field, author, work, commit_hash)

        if manifest is None:
            continue

        data.append(manifest)

    return data


def store_path(field, author, work):
    path = 'v1/manifests/{field}/{cluster}/{author}/{work}/manifest.json'.format(
        field=field,
        cluster=cluster_name(author),
        author=author,
        work=work
    )
    return path

def get_manifest(field, author, work, commit_hash):
    store_root = app.config['STORE_ROOT']
    path = store_path(field, author, work)

    blob_info = git.ls_tree(commit_hash, path)
    if blob_info == '':
        return None

    blob_hash = blob_info.split()[2]
    blob_content = git.cat_file('-p', blob_hash)

    blockchain_data = dict()
    for service in ['ethereum', 'bitcoin']:
        record_path = '{root}/v1/blockchains/{cluster}/{commit}/{service}/record.json'.format(
            root=store_root,
            cluster=cluster_name(commit_hash),
            commit=commit_hash,
            service=service
        )
        if os.path.exists(record_path):
            with open(record_path, 'r') as f:
                record_content = f.read()
            blockchain_data[service] = json.loads(record_content)

    timestamp = git.show('-s','--pretty=format:%ct', commit_hash)

    return dict(
        manifest=json.loads(blob_content),
        pistis=dict(
            hash=commit_hash,
            timestamp=timestamp,
        ),
        blockchain=blockchain_data
    )


@app.template_filter('utc')
def utc_filter(timestamp_str):
    epoch = float(timestamp_str)
    date = datetime.fromtimestamp(epoch, timezone.utc)
    return date.strftime("%d %b %Y %H:%M:%S %Z")
