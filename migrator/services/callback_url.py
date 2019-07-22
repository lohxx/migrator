#!/usr/bin/env python3
from flask import request

import pdb; pdb.set_trace()

from migrator import app
from migrator.models.tokens import Tokens


@app.route('/callback')
def callback():
    if request.args.get('code'):
        user_tokens = Tokens.query.one()
        user_tokens.save(request)
        os.environ['SPOTIFY_CODE'] = request.args['code']
        print(request.args['code'])

    return 'code'


#if __name__ == '__main__':
#    migrator.app.run()
