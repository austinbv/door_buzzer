from bottle import  Bottle, template, request
from gevent import Timeout
import gevent

class GPIOFake(object):
  @classmethod
  def output(*args):
    pass

import RPi.GPIO as GPIO
g = None

try:
  GPIO.setmode(GPIO.BCM)
  GPIO.setup(23, GPIO.OUT)
except:
  GPIO = GPIOFake

app = Bottle()

html = """
<html>
<head>
  <title>Open Me!</title>
  <link href="//netdna.bootstrapcdn.com/bootstrap/3.0.0/css/bootstrap.min.css" rel="stylesheet">
  <script src="//code.jquery.com/jquery-2.0.3.min.js"></script>
  <script type="text/javascript">
    $(function() {
      var ws = new WebSocket("ws://" + window.location.host + "/websocket");
      webskt = ws
      ws.onopen = function() {
          ws.send("Hello, world");
      };

      ws.onmessage = function (evt) {
          console.log(evt.data);
      };

      $('button').mouseup(function(){
        ws.send("lock");
      });

      $('button').mousedown(function(){
        ws.send("unlock");
      });
    });
  </script>
  <style>
    .container {
      text-align: center;
    }
     
    .container:before {
      content: '';
      display: inline-block;
      height: 100%;
      vertical-align: middle;
      margin-right: -0.25em;
    }

    .row {
      display: inline-block;
      vertical-align: middle;
      width: 100%;
    }
  </style>
</head>
<body style="padding-top: 20px">
  <div class="container">
    <div class="row">
      <img src="http://placehold.it/500x500"
    </div>
    <div class="row">
      <div class="col-md-offset-3 col-md-6">
        <button class="btn-lg btn-block btn-danger">Let em in</button>
      </div>
    </div>
  </div>
</body>
</html>
"""

def unlock_door():
  GPIO.output(23, True)

def lock_door():
  GPIO.output(23, False)

@app.route('/')
def hello():
    return template(html)

@app.route('/websocket')
def websocket():
  global g
  wsock = request.environ.get('wsgi.websocket')
  while True:
    try:
      message = wsock.receive()
      if message == "unlock":
        if g is not None:
          g.kill()
        unlock_door()
        g = gevent.spawn_later(5, lock_door)
      elif message == "lock":
        lock_door()
      wsock.send("Your message was: %r" % message)
    except WebSocketError:
      break

from gevent.pywsgi import WSGIServer
from geventwebsocket import WebSocketHandler, WebSocketError
server = WSGIServer(("0.0.0.0", 8080), app, handler_class=WebSocketHandler)
server.serve_forever()
