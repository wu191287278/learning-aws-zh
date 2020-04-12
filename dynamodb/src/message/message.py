from flask import Flask, render_template,request
from flask_socketio import SocketIO
import time
from datetime import datetime,timedelta
import random
import json
import boto3

app = Flask(__name__,static_url_path='')
app.config['SECRET_KEY'] = 'secret!'
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = timedelta(seconds=1)
socketio = SocketIO(app)

@app.route('/',methods=['GET'])
def index():
    return app.send_static_file('index.html')
    
if __name__ == '__main__':
    socketio.run(app)
    