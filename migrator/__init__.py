#!/usr/bin/env python3
import sys
import os

from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/tokens.db'
db = SQLAlchemy(app)


sys.path.append(os.getcwd())