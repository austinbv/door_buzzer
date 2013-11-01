#! /usr/bin/env python
import os

from bottle import Bottle, template, request, static_file
import bottle
from gevent.pywsgi import WSGIServer
from geventwebsocket import WebSocketHandler, WebSocketError
import gevent

script_path = os.path.abspath(__file__)
bottle.TEMPLATE_PATH.insert(0, "%s/../views" % script_path)

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


def unlock_door():
  GPIO.output(23, True)


def lock_door():
  GPIO.output(23, False)


@app.route('/')
def hello():
  return template('index')


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
  return static_file(path, '%s/../public' % script_path)

if __name__ == "__main__":
  port = int(os.environ.get('PORT', 80))
  server = WSGIServer(("0.0.0.0", port), app, handler_class=WebSocketHandler)
  server.serve_forever()
