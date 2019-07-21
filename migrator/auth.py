#!/usr/bin/env python3

import os

from flask import request

from migrator.migrator import app


@app.route('/callback')
def callback():
    if request.args.get('code'):
        os.environ['SPOTIFY_CODE'] = request.args['code']
        print(request.args['code'])

    return 'code'
