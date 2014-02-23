csrv.Card = function() {
  this.gameId = null;
  this.set = null;
  this.isRezzed = null;
  this.advancementTokens = null;
  this.agendaCounters = null;
  this.virusCounters = null;
  this.choices = [];
  this.div = null;
  this.menu = null;
  this.credits = 0;
  this.tooltip = false;
  this.host = null;
  this.hostedCards = [];
};

csrv.Card.prototype.update = function(cardState) {
  if (this.gameId && this.gameId != cardState['game_id']) {
    // card gameId doesnt match registry - wtf?
    delete csrv.gameRegistry[this.gameId];
  }
  this.gameId = cardState['game_id'];
  this.set = cardState['set'];
  this.number = cardState['number'];
  this.name = csrv.game.localization.cards[cardState['name']] || cardState['name'];
  this.isFaceup = cardState['is_faceup'];
  this.isRezzed = cardState['is_rezzed'];
  this.advancementTokens = cardState['advancement_tokens'];
  this.agendaCounters = cardState['agenda_counters'];
  this.credits = cardState['credits'];
  this.virusCounters = cardState['virus_counters'];
  this.choices = [];
  this.activeRun = false;
  this.host = cardState['host'];
  this.hostedCards = cardState['hosted_cards'] || [];

  // Save to the game registry
  self = this;
  csrv.gameRegistry[this.gameId] = self;
};

csrv.Card.prototype.imagePath = function() {
  if (this.set != null && this.number != null) {
    return '/static/images/' + csrv.zeroPad(this.set, 2) +
      csrv.zeroPad(this.number, 3) + '.png';
  }
  return null;
};

csrv.Card.prototype.hilight = function() {
  if (this.div) {
    this.div.addClass('hilight');
  }
};

csrv.Card.prototype.unhilight = function() {
  if (this.div) {
    this.div.removeClass('hilight');
  }
};

csrv.Card.prototype.addChoice = function(choice) {
  this.choices.push(choice);
};

csrv.Card.prototype.removeChoice = function(choice) {
  this.choices.splice(this.choices.indexOf(choice), 1);
  this.removeContextMenu();
  if (this.choices.length == 0 && this.div) {
    this.unhilight();
    this.div.attr('title', null);
    this.div.unbind('dblclick');
  }
};

csrv.Card.prototype.clearChoices = function() {
  var choices = this.choices.slice(0);
  for (var i = 0; i < choices.length; i++) {
    var choice = choices[i];
    this.removeChoice(choice);
  }
};

csrv.Card.prototype.addDoubleClickHandler = function() {
  var choice = this.choices[0];
  this.div.attr('title', null);
  this.div.attr('title', choice.descriptionHtml());
  this.div[0].title = choice.descriptionHtml();
  saveDiv = this.div
  this.div.dblclick(function() {
    choice.resolve();
  });
};

csrv.Card.prototype.addContextMenu = function() {
  var self = this;
  var items = {};
  for (var i = 0; i < this.choices.length; i++) {
    items[i] = {
      name: this.choices[i].descriptionHtml()
    };
  }

  $.contextMenu({
    autoHide: true,
    trigger: 'left',
    selector: '[data-gameId=' + this.gameId + ']',
    items: items,
    callback: function(key, options) {
      self.onMenuChoice(key, options);
    }
  });
  this.menu = true;
};

csrv.Card.prototype.onMenuChoice = function(key, options) {
  this.choices[key].resolve();
};

csrv.Card.prototype.removeContextMenu = function() {
  if (this.menu) {
    this.menu = false;
    $.contextMenu('destroy', '[data-gameId=' + this.gameId + ']');
  }
};

csrv.Card.prototype.buildDiv = function() {
  var div = $('<div>', {
    'class': 'card',
    'data-gameId': this.gameId,
    'data-name': this.name});
  this.setDivImage(div);
  var self = this;

  div.mouseenter(function(evt) {
    var viewer = $('#card_viewer');
    viewer.empty();
    if (self.number) {
      viewer.stop(true, true).fadeIn();
      viewer.append($('<img>', {src: self.imagePath()}));
    }
  });

  div.mouseleave(function(evt) {
    var viewer = $('#card_viewer');
    var img = viewer.children('img');
    if (img.attr('src') == self.imagePath()) {
      viewer.stop(true, true).fadeOut();
    }
  });

  return div;
};

csrv.Card.prototype.setDivImage = function(div) {
  div.css({
    'background': this.imagePath() ? 'url(' + this.imagePath() + ')' : null,
    'background-size': '75px 105px',
    'background-repeat': 'no-repeat'
  });
  if (this.isRezzed == false) {
    div.addClass('facedown');
    if (!div.children('img').length) {
      div.append($('<img>', {src: '/static/images/corp-back.jpg'}));
    }
  } else {
    div.removeClass('facedown');
    var img = div.children('img');
    if (img.length) {
      if (img.attr('src') != '/static/images/transparent.gif') {
        img.attr('src', '/static/images/transparent.gif');
      }
    } else {
      div.append($('<img>', {src: '/static/images/transparent.gif'}));
    }
  }
};

/*
 * Render html element for this card. Parent is responsible for placing it.
 **/
csrv.Card.prototype.render = function() {
  if (!this.div) {
    this.div = this.buildDiv();
  } else {
    this.setDivImage(this.div);
  }
  if (this.activeRun) {
    this.div.addClass('run');
  } else {
    this.div.removeClass('run');
  }
  if (this.choices.length > 0) {
    this.hilight();
  }
  if (this.choices.length > 1 && !this.menu) {
    this.addContextMenu();
  } else if (this.choices.length == 1) {
    this.addDoubleClickHandler();
  }

  this.renderTokens();
  var self = this;
};

csrv.Card.prototype.renderHost = function() {
  if (this.host) {
    var hostCard = csrv.gameRegistry[this.host];
    this.div.position({
      my: 'center',
      at: 'center',
      of: hostCard.div.children('img'),
      collision: 'fit'
    });
  }
};

csrv.Card.prototype.renderHosted = function() {
  if (this.hostedCards.length) {
    var offset = 0;
    for (var i = 0; i < this.hostedCards.length; i++) {
      var card = csrv.gameRegistry[this.hostedCards[i]];
      if (!card.div) {
        card.render();
      }
      card.div.position({
        my: 'right bottom',
        at: 'center+' + offset + '%',
        of: this.div,
        collision: 'none'
      });
      offset += 40;
    }
  }
};

csrv.Card.prototype.addTrashIcon = function() {
  var trashDiv = $('<div>', {'class': 'trash'});
  trashDiv.append($('<img>', {src: '/static/images/redx.png'}));
  this.div.append(trashDiv);
};

csrv.Card.prototype.removeTrashIcon = function() {
  var trashDiv = this.div.children('.trash');
  if (trashDiv) {
    trashDiv.remove();
  }
};

/**
 * Create and populate the card's token layer.
 */
csrv.Card.prototype.renderTokens = function() {
  if (!this.tokenDiv) {
    this.tokenDiv = $('<div>', {'class': 'token'});
    this.div.append(this.tokenDiv);
  }
  this.renderAdvancementTokens();
  this.renderCredits();
  this.renderVirusCounters();
};

csrv.Card.prototype.renderTokenType = function(cssClass, imgPath, value, div) {
  var tokens = this.tokenDiv.children('.' + cssClass);
  if (tokens.length < value) {
    var toAdd = value - tokens.length;
    for (var i = 0; i < toAdd; i++) {
      var img = $('<img>', {src: imgPath, 'class': cssClass});
      div.append(img);
    }
  } else if (tokens.length > value) {
    var toRemove = tokens.length - value;
    for (var i = 0; i < toRemove; i++) {
      tokens[i].remove();
    }
  }
};


csrv.Card.prototype.renderAdvancementTokens = function() {
  this.renderTokenType(
      'advancement',
      '/static/images/advancement.png',
      this.advancementTokens,
      this.tokenDiv);
};

csrv.Card.prototype.renderCredits = function() {
  this.renderTokenType(
      'credit',
      '/static/images/credit_token.png',
      this.credits,
      this.tokenDiv);
};

csrv.Card.prototype.renderVirusCounters = function() {
  this.renderTokenType(
      'virus_counter',
      '/static/images/virus_counter.png',
      this.virusCounters,
      this.tokenDiv);
};

csrv.Card.prototype.unrender = function() {
  if (this.div) {
    this.div.remove();
    this.div = null;
  }
};

/*
 * Unrender and remove this card from registry.
 */
csrv.Card.prototype.remove = function() {
  this.unrender();
  delete csrv.gameRegistry[this.gameId];
};
