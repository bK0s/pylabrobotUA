from flask import Flask
from flask_socketio import SocketIO, send, emit
import json


app = Flask(__name__)
socketio = SocketIO(app)

@app.route('/')
def index():

  return json.dumps({"msg": "test"})

@app.route('/ping')
def ping():
  return json.dumps({"msg": "pong"})


if __name__ == "__main__":
  socketio.run(app, debug=True)
