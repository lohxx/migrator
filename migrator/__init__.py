#!/usr/bin/env python3
import sys
import os

from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/tokens.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


sys.path.append(os.getcwd())


@app.route('/callback')
def callback():
    from models import tokens

    if request.args.get('code'):
        # user_tokens = tokens.save_tokens(request)
        # tokens.Tokens.query.filter_by(
        #     service=tokens.SPOTIFY).one()
        # user_tokens.save(request)

        print(request.args['code'])

    return 'code'


if __name__ == '__main__':
    app.run(debug=True)