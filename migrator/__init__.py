#!/usr/bin/env python3
import os
import sys

from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/migrator.db'

db = SQLAlchemy(app)
db.init_app(app)


@app.route('/callback')
def callback():
    from migrator.services.tokens import save_tokens
    import pdb; pdb.set_trace()
    if request.args.get('code'):
        save_tokens(1, request.args)

    return 'Codigo salvo com sucesso'


if __name__ == '__main__':
    app.run(debug=True)
