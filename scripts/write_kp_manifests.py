#!/usr/bin/env python3

"""
load db site_data_source.db

> .table

    Collection
    Indexes
    SystemInfo
    _a_dataSourceUsernameIndex
    _a_sitename_a_usernameIndex
    _a_username_a_dataSourceId_a_projectNameIndex
    _a_username_a_dataSourceName_a_projectNameIndex
    _a_username_a_pagesizeIndex
    _a_username_a_projectNameIndex
    _a_username_a_sitenameIndex

> .schema _a_username_a_sitenameIndex

    CREATE TABLE _a_username_a_sitenameIndex (cid INTEGER UNIQUE PRIMARY KEY, name1 BLOB,name2 BLOB);

> select * from _a_username_a_sitenameIndex;

    ......
    ......
    28403|yin670769755|__keepwork__
    28404|sanzhaizhai|__keepwork__
    28405|qq2389527979|__keepwork__
    28406|zhy981224|__keepwork__
    28407|wt754495353|__keepwork__
    28408|littleduoo|__keepwork__
    28409|lina210|__keepwork__
    28410|ryan|biaoqingbao
    28411|board|__keepwork__
    28412|dftest1001|0986743121234561521513122625
    28413|dftest1001|0986743121234561521513150267
    28414|dftest1001|0986743121221521513159778
    28415|ljy19991221|__keepwork__
    28416|dftest0007|fashunfeng1521513615451
    28417|choi|123

loop all entries:
- cid: id in Collection
- name1: username
- name2: sitename

> select value from Collection where id = cid;

    {updateFlag=0,dataSourceId=158,sitename="__keepwork__",projectId=403,rootPath="",dataSourceName="内置gitlab",username="wxaxiaoyao",lastCommitId="c1095b1c1bc97197894ea0446e42f27efd533401",projectName="keepworkdatasource",}

grep lastCommitId


pattern:

    url: keepwork.com/dreamanddead/opsway
      - username: dreamanddead
      - sitename: opsway  (exclude __keepwork__)

    POST
    - field: keepwork
    - author: ${username}
    - work: ${sitename}
    - identity: ${lastCommitId}
"""

import sqlite3
import re
import requests
import logging
import json
import argparse
import os

logging.basicConfig(level=logging.INFO)

def vips():
    conn = sqlite3.connect(os.path.join(DBDIR, 'vip.db'))
    c = conn.cursor()

    author_re = re.compile(r'username="(.*?)",')
    for row in c.execute('''select value from Collection where value like "%isValid=true%"'''):
        (data,) = row

        result = author_re.search(data)
        if result is not None:
            yield result.group(1)
        else:
            continue

    conn.close()


def works():
    vip_set = set(vips())

    conn = sqlite3.connect(os.path.join(DBDIR, 'site_data_source.db'))
    c = conn.cursor()

    identity_re = re.compile(r'lastCommitId="(.*?)",')
    for row in c.execute('''select name1, name2, value
                            from _a_username_a_sitenameIndex, Collection
                            where _a_username_a_sitenameIndex.cid = Collection.id'''):
        (author, work, data) = row

        if work == '__keepwork__':
            continue

        result = identity_re.search(data)
        if result is None:
            continue
        identity = result.group(1)
        if identity == 'master':
            continue

        if (author in vip_set) == VIP:
            yield (author, work, identity)

    conn.close()


def witness():
    api_addr = '%s/api/v1/manifest' % SERVER

    for author, work, identity in works():
        post_data = dict(
            field='keepwork',
            author=author,
            work=work,
            identity=identity,
        )
        r = requests.post(api_addr, json=post_data)

        if not r.ok:
            raise Exception("http request failed", post_data)

        if 'error' in r.json():
            raise Exception("response error", r.json()['error'])

        logging.info('upload %s', json.dumps(post_data))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("server", help="pistis server address, e.g. http://localhost:5000/")
    parser.add_argument("-v", "--vip", help="vip users or not", action="store_true", default=False)
    parser.add_argument("-d", "--dbdir", help="dir that tabledb files locate", default='.')

    args = parser.parse_args()

    db_files = ['site_data_source.db', 'vip.db']
    for f in db_files:
        db_path = os.path.join(args.dbdir, f)
        if not os.path.exists(db_path):
            exit('%s not exists in dir %s' % (f, args.dbdir))
        if not os.access(db_path, os.R_OK):
            exit('%s in dir %s is not readable' % (f, args.dbdir))

    global DBDIR, VIP, SERVER

    DBDIR = args.dbdir
    SERVER = args.server.strip('/')
    VIP = args.vip

    witness()
