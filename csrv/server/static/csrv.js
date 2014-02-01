/* namespace */
var csrv = {};
csrv.gameState = null;
csrv.currentChoices = null;
csrv.defaultChoiceTimer = null;

csrv.init = function() {
  csrv.game = new csrv.Game();
  csrv.ws = new WebSocket(
      "ws://" + window.document.location.hostname + ":" +
      window.document.location.port + csrv.baseUrl + "/sock");

  csrv.ws.onopen = function (evt) { console.log('connected') };
  csrv.ws.onmessage = csrv.updateState;
  $(window).resize(function(evt) { csrv.game.renderHosted(); });
  csrv.createTooltip();
  csrv.setupInfoBar();
};

csrv.createTooltip = function() {
  $(document).tooltip({
    content: function() {
      var element = $(this);
      return element.attr('title');
    }
  });
};

csrv.destroyTooltip = function() {
  $(document).tooltip('destroy');
};

csrv.setupInfoBar = function() {
  if (csrv.side == 'corp') {
    $('#corp_info').insertBefore('#choices');
  } else {
    $('#runner_info').insertBefore('#choices');
  }
};

csrv.showModal = function(message) {
  $('#dialog').empty();
  $('#dialog').append($('<pre>', {text: message}));
  $('#dialog').dialog({
    modal: true,
    buttons: {
      Ok: function() {
        $(this).dialog('destroy');
      }
    }
  });
  $('#dialog').dialog('open');
};


csrv.updateState = function(evt) {
  var response = JSON.parse(evt.data);
  if ('error' in response) {
    console.log(response['error']);
    csrv.showModal(response['error']);
    csrv.game.render();
  } else if ('log' in response) {
    csrv.log = response;
    csrv.showMessages();
  } else {
    csrv.destroyTooltip();
    csrv.gameState = response;
    csrv.game.update(csrv.gameState);
    csrv.game.render();
    csrv.game.renderHosted();
    csrv.createTooltip();
  }
};

csrv.showMessages = function() {
  var messages = $('#messages')[0];
  for (var i = 0; i < csrv.log['log'].length; i++) {
    var message = $('<p>', {text: '> ' + csrv.log['log'][i]['message']});
    message.css('display', 'none');
    $(messages).append(message);
    message.fadeIn('slow');
    messages.scrollTop = messages.scrollHeight - messages.clientHeight;
  }
};

csrv.clearDefaultChoice = function() {
  if (csrv.defaultChoiceTimer) {
    clearTimeout(csrv.defaultChoiceTimer);
    csrv.defaultChoiceTimer = null;
  }
};

csrv.setDefaultChoiceTimer = function() {
  setTimeout(function() {
    $('#choices').empty();
    $('#choices').append($('<h3>', {text: 'Nothing to do. passing'}));
    csrv.sendChoice(null)
  }, 2000);
};

csrv.zeroPad = function(number, length) {
    var numberStr = number.toString();
    var numberLen = numberStr.length;
    for (var i = 0; i < length - numberLen; i++) {
        numberStr = '0' + numberStr;
    };
    return numberStr;
};

csrv.onFadeClick = function(event) {
    /* Show the original element again */
    event.data[0].css('opacity', '100');
    event.data[1].remove();
    $('#overlay').css('display', 'none');
    $('#fade').css('display', 'none');
};

csrv.onCardClick = function(event) {
    img = $(event.target);
    src = img.attr('src');
    csrv.showOverlay(img, $('<img>', {'src': src}));
};

csrv.showOverlay = function(original, temp) {
    /* Hide the original element */
    original.css('opacity', '0');
    $('#fade').click([original, temp], csrv.onFadeClick);
    temp.appendTo($('#overlay'));
    $('#overlay').css('display', 'block');
    $('#fade').css('display', 'block');
};

csrv.onUnrezzedCardClick = function(event) {
  var div = $(event.target).parent();
  var url = $(event.target).parent().css('background-image');
  /* pull the image url out of a url('xxxx') string */
  url = url.replace(/^url\(["']?/, '').replace(/["']?\)$/, '');
  csrv.showOverlay(div, $('<img>', {'src': url}));
};

csrv.onIceClick = csrv.onUnrezzedCardClick;

