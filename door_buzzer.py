#! /usr/bin/env python
import os

from bottle import  Bottle, template, request, static_file
from gevent import Timeout
from gevent.pywsgi import WSGIServer
from geventwebsocket import WebSocketHandler, WebSocketError
import gevent

class GPIOFake(object):
  @classmethod
  def output(*args):
    pass

current_press = None

try:
  import RPi.GPIO as GPIO
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
  <script src="/public/zepto.js"></script>
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
        $(this).addClass('btn-danger').removeClass('btn-success');
        $('#lock').addClass('locked');
      });

      $('button').mousedown(function(){
        ws.send("unlock");
        $('#lock').removeClass('locked');
        $(this).removeClass('btn-danger').addClass('btn-success');
      });

      $("#lock").load('/public/lock.svg',function(){
        var that = this;
        setTimeout(function(){$(that).addClass("locked");} ,0)
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

    button.btn-lg {
      outline: 0;
      font-size: 72px;
    }

    #lock {
      width: 100px;
      height: 70px;
      display: inline-block;
    }

    #lock #bar {
      -webkit-transform: rotateY(0deg);
      -webkit-transform-origin: 85% 60%;
      -webkit-transition: -webkit-transform 0.5s;
    }

    #lock.locked #bar {
      -webkit-transform: rotateY(180deg);
    }
  </style>
</head>
<body style="padding-top: 20px">
  <div class="container">
    <div class="row">
      <div class="col-md-offset-2 col-md-9">
        <img id="stream" src="http://10.66.10.3/mjpg/video.mjpg" width="640" height="480" border="0" alt="If no image is displayed, there might be too many viewers, or the browser configuration may have to be changed. See help for detailed instructions on how to do this.">
        <button class="btn-lg btn-block btn-danger">
          Let em in
          <div id="lock"></div>
        </button>
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
  global current_press
  wsock = request.environ.get('wsgi.websocket')
  while True:
    try:
      message = wsock.receive()
      if message == "unlock":
        if current_press is not None:
          current_press.kill()
        unlock_door()
        current_press = gevent.spawn_later(5, lock_door)
      elif message == "lock":
        lock_door()
      wsock.send("Your message was: %r" % message)
    except WebSocketError:
      break

@app.route('/public/<path:path>')
def callback(path):
    return static_file(path, 'public')

if __name__ == "__main__":
  port = int(os.environ.get('PORT', 80))
  server = WSGIServer(("0.0.0.0", port), app, handler_class=WebSocketHandler)
  server.serve_forever()
