import os

from flask import Flask
from flask import request

app = Flask(__name__)

@app.route('/callback')
def callback():
    if request.args.get('code'):
        os.environ['SPOTIFY_CODE'] = request.args['code']
        print(request.args['code'])

    return 'code'



if __name__ == '__main__':
    app.run()