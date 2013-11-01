$(function () {
  var ws = new WebSocket("ws://" + window.location.host + "/websocket");

  ws.onopen = function () {
    ws.send("Hello, world");
  };

  ws.onmessage = function (evt) {
    console.log(evt.data);
  };

  function stopEvents(e) {
    e.preventDefault();
    e.stopPropagation();

    if (e.gesture) {
      e.gesture.preventDefault();
      e.gesture.stopPropagation();
    }
  }

  function lock(e) {
    stopEvents(e);
    ws.send("lock");
    $(this).addClass('btn-danger').removeClass('btn-success');
    $('#lock').addClass('locked');
  }

  function unlock(e) {
    stopEvents(e);
    ws.send("unlock");
    $('#lock').removeClass('locked');
    $(this).removeClass('btn-danger').addClass('btn-success');
  }

  $('button').on('mouseup', lock);
  $('button').on('mousedown', unlock);
  Hammer($('button')[0]).on('touch', unlock);
  Hammer($('button')[0]).on('release', lock);

  $("#lock").load('/public/lock.svg', function () {
    var that = this;
    setTimeout(function () {
      $(that).addClass("locked");
    }, 0)
  });
});
