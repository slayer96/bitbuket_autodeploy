import subprocess as sp
from pathlib import Path
from flask import Flask, Response, request
import pdb
import os

PREFIX = '/home/ubuntu/projects/{}'

app = Flask(__name__)


@app.route('/')
def readme():
    return Response(open('readme.md'), content_type='text/plain;charset=utf-8')


@app.route('/webhook', methods=('POST',))
def wb():
    PREFIX = '/home/ubuntu/projects/{}'
    data = request.get_json(force=True)
    print(data)
    if not data:
        return Response('No data found.'), 404
    br = get_branch(data)
    if br is None:
        return Response('No new changes found.'), 403
    repo = data['repository']['name']
    if repo == 'amazon_research_tool':
        repo = 'rst'
    if repo == 'amazon_scanner':
        PREFIX = '/home/ubuntu/projects/amazon_api/{}'
    wd = PREFIX.format(repo)
    p = Path(wd)
    if not p.exists() or not p.is_dir():
        return Response('Project not found.'), 403

    out = 'Project path: {}\n'.format(wd)
    args = (
	'pwd',
        'git pull',
        'pip install -r requirements.txt',
        #'sudo systemctl restart amazon-api-worker'.split(),
        #'sudo systemctl restart amazon-api'.split(),
    )
    # pdb.set_trace()
    print('Project path: {}\n'.format(wd))
    for x in args:
        print(x)
        print(repo, wd)
        # os.chdir(wd)
        cp = sp.run(x, cwd=wd, shell=True, stdout=sp.PIPE, stderr=sp.STDOUT, universal_newlines=True, executable='/bin/bash')
        out += cp.stdout
        print(out)
        if cp.returncode:
            return Response(out), 500

    return Response(out)


def get_branch(data):
    if 'ref' in data:
        # GitHub webhook
        return data['ref'].split('/')[-1]

    # Bitbucket webhook
    sq = [x for x in data['push']['changes']
          if 'new' in x and x['new'] and x['new']['type'] == 'branch']
    try:
        return sq[0]['new']['name']
    except (IndexError, KeyError):
        return None


if __name__ == '__main__':
    app.run(port=7000, host='0.0.0.0', debug=True)

