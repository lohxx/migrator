#!/usr/bin/env python3
import os
import sys

from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URI']

db = SQLAlchemy(app)
db.init_app(app)


@app.route('/deezer/callback')
def deezer_callback():
    from migrator.services.tokens import save_tokens
    import pdb; pdb.set_trace()
    if request.args.get('code'):
        save_tokens(2, request.args)

    return 'deezer'


@app.route('/spotify/callback')
def spotify_callback():
    from migrator.services.tokens import save_tokens
    if request.args.get('code'):
        save_tokens(1, request.args)

    return "token salvo"


def init_db():
    """ Inicializa o banco de dados """
    from migrator.services.tokens import TokensManager
    db.create_all()


if __name__ == '__main__':
    app.run(debug=True)