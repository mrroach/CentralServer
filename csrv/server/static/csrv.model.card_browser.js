csrv.CardBrowser = function() {
  this.div = $('#card_browser');
};

csrv.CardBrowser.prototype.show = function(options) {
  options = $.extend({
    message: 'Browse cards',
    cards: [],
    callback: function(chosenIds) {},
    renderCopy: true,
    buttonText: 'Ok',
    allowSelect: true,
    sortable: false
  }, options || {});
  this.div.empty();
  var browser = $('<div>', {'class': 'card-list'});
  browser.appendTo(this.div);
  console.log('reading card list');
  for (var i = 0; i < options['cards'].length; i++) {
    if (options['renderCopy']) {
      var cardDiv = options['cards'][i].buildDiv();
      browser.append(cardDiv);
    } else {
      options['cards'][i].render();
      var cardDiv = options['cards'][i].div;
    }
    if (options['allowSelect']) {
      cardDiv.click(function(evt) {
        $(evt.currentTarget).toggleClass('chosen');
      });
    }
    if (options['sortable']) {
      this.div.children('.card-list').sortable();
    }
  }
  console.log('opening dialog');
  this.openDialog(options);
};

csrv.CardBrowser.prototype.openDialog = function(options) {
  if (options['sortable']) {
    var buttonOpts = {
      text: options['buttonText'],
      click: this.buildSortCallback(options['callback'])
    };
  } else {
    var buttonOpts = {
      text: options['buttonText'],
      click: this.buildCallback(options['callback'])
    };
  }
  this.div.dialog({
    title: options['message'],
    buttons: [buttonOpts],
    maxWidth: 800,
    maxHeight: 500
  });
  this.div.dialog('open');
};

csrv.CardBrowser.prototype.buildCallback = function(callback) {
  console.log('building callback');
  return function(event) {
    var chosen = $('#card_browser .card.chosen');
    $('#card_browser').dialog('close');
    var chosenIds = [];
    for (var i = 0; i < chosen.length; i++) {
      chosenIds.push($(chosen[i]).attr('data-gameId'));
    }
    $('#card_browser').dialog('destroy');
    callback(chosenIds);
  };
};

csrv.CardBrowser.prototype.buildSortCallback = function(callback) {
  return function(event) {
    var cards = $('#card_browser .card');
    $('#card_browser').dialog('close');
    var cardIds = [];
    for (var i = 0; i < cards.length; i++) {
      cardIds.push($(cards[i]).attr('data-gameId'));
    }
    $('#card_browser').dialog('destroy');
    callback(cardIds);
  };
};
