from bottle import  Bottle, template, request
from gevent import Timeout
import gevent

class GPIOFake(object):
  @classmethod
  def output(*args):
    pass

import RPi.GPIO as GPIO
current_press = None

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
      <div class="col-md-offset-2 col-md-9">
	<img id="stream" src="http://10.66.10.3/mjpg/video.mjpg" width="640" height="480" border="0" alt="If no image is displayed, there might be too many viewers, or the browser configuration may have to be changed. See help for detailed instructions on how to do this.">
	<!-- <iframe src="http://10.66.10.3" height="600" width="800"></iframe> -->
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
	print g
        if current_press is not None:
	  print "inside"
          g.kill()
        unlock_door()
        current_press = gevent.spawn_later(5, lock_door)
      elif message == "lock":
        lock_door()
      wsock.send("Your message was: %r" % message)
    except WebSocketError:
      break

from gevent.pywsgi import WSGIServer
from geventwebsocket import WebSocketHandler, WebSocketError
server = WSGIServer(("0.0.0.0", 80), app, handler_class=WebSocketHandler)
server.serve_forever()
