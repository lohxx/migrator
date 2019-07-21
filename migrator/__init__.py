#!/usr/bin/env python3
import os
import sys

from auth import *
from flask import Flask

sys.path.append(os.path.dirname(os.path.realpath(__file__)))


app = Flask(__name__)


if __name__ == '__main__':
    app.run()
