#!/usr/bin/env python3
from flask import request

from migrator import app
from migrator.models import tokens


@app.route('/callback')
def callback():

    if request.args.get('code'):
        user_tokens = tokens.Tokens.query.filter_by(
            service=tokens.SPOTIFY).one()
        user_tokens.save(request)
        os.environ['SPOTIFY_CODE'] = request.args['code']
        print(request.args['code'])

    return 'code'


#if __name__ == '__main__':
#    migrator.app.run()
