// Cards/servers should register themselves by game id here

/** Holds a mapping of game ids to objects (cards, servers) **/
csrv.gameRegistry = {};

/**
 * @constructor
 * Defines the root object of the game data tree.
 * The game object builds all its children and updates/renders them.
 * @this {csrv.Game}
 * @param {Object} gameState The parsed json data representing the game.
 */
csrv.Game = function(gameState) {
  this.choiceCount = -1;
  this.runner = new csrv.Runner();
  this.corp = new csrv.Corp();
  this.choices = new csrv.Choices(this);
  this.run = new csrv.Run();
  this.localization = new csrv.CardLocalization();
};

/**
 * Render game elements.
 * @this {csrv.Game}
 */
csrv.Game.prototype.render = function() {
  this.corp.render();
  this.runner.render();
  this.run.render();
  this.choices.render();
};

csrv.Game.prototype.renderHosted = function() {
  this.corp.renderHosted();
  this.runner.renderHosted();
};

/**
 * Update the game state and propagate changes to children.
 * @param {Object} gameState The parsed json gamestate.
 */
csrv.Game.prototype.update = function(gameState) {
  this.gameState = gameState;
  console.log(this.choiceCount + ' ' + gameState['choice_count']);
  this.choiceCount = gameState['choice_count'];
  this.corp.update(gameState['corp']);
  this.runner.update(gameState['runner']);
  this.run.update(gameState['run']);
  this.choices.update(gameState['choices']);
};

csrv.Run = function() {
  this.accessedCards = [];
  this.cards = {};
  this.server = null;
  this.ice = null;
};

csrv.Run.prototype.update = function(runState) {
  var runState = runState || {};
  if (runState['server'] != this.server) {
    if (!this.server) {
      csrv.game.choices.fastModeDisable();
    }
    var server = csrv.gameRegistry[this.server];
    if (server) {
      server.activeRun = false;
      server.beingAccessed = false;
    }
    this.server = runState['server'];
    var server = csrv.gameRegistry[this.server];
    if (server) {
      server.activeRun = true;
    }
  }
  if (this.ice && (runState['current_ice'] || {})['game_id'] != this.ice) {
    var ice = csrv.gameRegistry[this.ice];
    if (ice) {
      ice.activeRun = false;
    }
  }
  this.ice = (runState['current_ice'] || {})['game_id'];
  var ice = csrv.gameRegistry[this.ice];
  if (ice) {
    ice.activeRun = true;
  }
  this.accessedCards = runState['accessed_cards'] || [];
  this.currentIce = runState['current_ice'];
};

csrv.Run.prototype.setServerAccess = function() {
  var server = csrv.gameRegistry[this.server];
  if (server) {
    server.beingAccessed = true;
  }
};

csrv.Run.prototype.render = function() {
  $('#accessed_cards').empty();
  for (var i = 0; i < this.accessedCards.length; i++) {
    var cardState = this.accessedCards[i];
    var card = csrv.gameRegistry[cardState['game_id']];
    if (card) {
      if (card.div) {
        var cardDiv = null;
      } else {
        var cardDiv = card.buildDiv();
      }
    } else {
      card = new csrv.Card();
      card.update(cardState);
      var cardDiv = card.buildDiv();
      card.remove();
    }
    if (cardDiv) {
      $('#accessed_cards').append(cardDiv);
    }
  }

  if (this.accessedCards.length) {
    $('#accessed_cards').css('display', 'block');
  } else {
    $('#accessed_cards').css('display', 'none');
  }
};

/**
 * Build a new array, keeping any existing card objects and creating new ones.
 * @param {Object} parent The parent game object (Hand, Server, etc.) for cards.
 * @param {Array} current An array of csrv.Card objects.
 * @param {Array} desired An array of card gameState objects.
 * @return {Array}
 */
csrv.updateCardArray = function(parent, current, desired, skipCheck) {
  current = current || [];
  var newArray = [];

  for (var i = 0; i < desired.length; i++) {
    var card = null;
    for (var j = 0; j < current.length; j++) {
      if (current[j].gameId == desired[i]['game_id']) {
        card = current.splice(j, 1)[0];
        break;
      }
    }
    if (!card) {
      if (!skipCheck || (skipCheck && !skipCheck(desired[i]))) {
        card = new csrv.Card();
      }
    }
    if (card) {
      card.parent = parent;
      card.update(desired[i]);
      newArray.push(card);
    }
  }
  // Get rid of any extra cards
  for (var i = 0; i < current.length; i++) {
    current[i].remove();
  }
  return newArray;
};

csrv.addToDiv = function(div, child) {
  if (false && csrv.side == 'runner') {
    div.prepend(child);
    prependedDiv = div;
  } else {
    div.append(child);
  }
};

csrv.addToDivReverse = function(div, child) {
  if (false && csrv.side == 'runner') {
    div.append(child);
  } else {
    div.prepend(child);
  }
};

csrv.renderCardsInParent = function(div, cards) {
  for (var i = 0; i < cards.length; i++) {
    cards[i].render();
    if (false && csrv.side == 'runner') {
      if (cards[i].div.index() != cards.length - i - 1) {
        csrv.addToDiv(div, cards[i].div);
      }
    } else {
      if (cards[i].div.index() != i) {
        csrv.addToDiv(div, cards[i].div);
        cards[i].div.effect('hilight', 'slow');
      }
    }
  }
};

csrv.Corp = function(game) {
  this.game = game;
  this.archives = new csrv.Server({serverType: 'archives'});
  this.rnd = new csrv.Server({serverType: 'rnd'});
  this.hq = new csrv.Server({serverType: 'hq'});
  this.remotes = {};
  this.hand = new csrv.CorpHand();
  this.agendaPoints = 0;
  this.badPublicity = 0;
  this.clicks = 0;
  this.credits = 0;
  this.corpState = null;
};

csrv.Corp.prototype.update = function(corpState) {
  this.corpState = corpState;

  this.clicks = corpState['clicks'];
  this.agendaPoints = corpState['agenda_points'];
  this.badPublicity = corpState['bad_publicity'];
  this.credits = corpState['credits'];
  this.hand.update(corpState['hq']['cards']);

  this.archives.update(corpState['archives']);
  this.rnd.update(corpState['rnd']);
  this.hq.update(corpState['hq'], corpState['identity']);

  for (var i = 0; i < corpState['remotes'].length; i++) {
    var remote = corpState['remotes'][i];
    if (!(remote['game_id'] in this.remotes)) {
      this.remotes[remote['game_id']] = new csrv.Server();
    }
    this.remotes[remote['game_id']].update(remote);
  }
  // This is ugly and expensive. A set object would be nice
  var remoteKeys = Object.keys(this.remotes);
  for (var i = 0; i < remoteKeys.length; i++) {
    var found = false;
    for (var x = 0; x < corpState['remotes'].length; x++) {
      if (corpState['remotes'][x]['game_id'] == remoteKeys[i]) {
        found = true;
      }
    }
    if (!found) {
      delete this.remotes[remoteKeys[i]];
    }
  }
};

csrv.Corp.prototype.render = function() {
  this.hand.render();
  this.archives.render();
  this.rnd.render();
  this.hq.render();
  var remoteKeys = Object.keys(this.remotes);
  for (var i = 0; i < remoteKeys.length; i++) {
    this.remotes[remoteKeys[i]].render();
  }
  var info = $('#corp_info');
  info.children('.clicks').html([
      $('<img>', {src: '/static/images/click.png'}), this.clicks]);
  info.children('.credits').html([
      $('<img>', {src: '/static/images/Credit.png'}), this.credits]);
  info.children('.hand_size').html([
      $('<img>', {src: '/static/images/hand.png'}),
      this.hand.cards.length]);
  info.children('.bad_publicity').html([
      $('<img>', {src: '/static/images/occupy.png'}), this.badPublicity]);
  info.children('.agendas').html([
      $('<img>', {src: '/static/images/chart.png'}),
      this.agendaPoints]);
};

csrv.Corp.prototype.renderHosted = function() {
  this.archives.renderHosted();
  this.hq.renderHosted();
  this.rnd.renderHosted();
  var remoteKeys = Object.keys(this.remotes);
  for (var i = 0; i < remoteKeys.length; i++) {
    this.remotes[remoteKeys[i]].renderHosted();
  }
};

csrv.Runner = function() {
  this.runnerState = null;
  this.hand = null;
  this.rig = null;
  this.stack = null;
  this.heap = null;
  this.hand = new csrv.RunnerHand();
  this.clicks = 0;
  this.credits = 0;
  this.agendaPoints = 0;
  this.link = 0;
  this.tags = 0;
  this.memory = 4;
  this.brainDamage = 0;
  this.identity = null;
};

csrv.Runner.prototype.update = function(runnerState) {
  this.runnerState = runnerState;

  this.credits = runnerState['credits'];
  if (csrv.side == 'corp' && this.clicks == 1 && runnerState['clicks'] == 0) {
    csrv.game.choices.fastModeDisable();
  }
  this.clicks = runnerState['clicks'];
  this.memory = runnerState['free_memory'];
  this.agendaPoints = runnerState['agenda_points'];
  this.tags = runnerState['tags'];

  this.rig = csrv.updateCardArray(this, this.rig, runnerState['rig']);
  this.stack = csrv.updateCardArray(this, this.stack, runnerState['stack']);
  this.heap = csrv.updateCardArray(this, this.heap, runnerState['heap']);
  this.heapDiv = null;
  this.hand.update(runnerState['grip']);
  if (!this.identity) {
    this.identity = new csrv.Card();
    this.identity.update(runnerState['identity']);
  }
};


csrv.Runner.prototype.render = function() {
  csrv.renderCardsInParent($('#rig'), this.rig);
  this.hand.render();
  var info = $('#runner_info');
  info.children('.clicks').html([
      $('<img>', {src: '/static/images/click.png'}), this.clicks]);
  info.children('.credits').html([
      $('<img>', {src: '/static/images/Credit.png'}), this.credits]);
  info.children('.hand_size').html([
      $('<img>', {src: '/static/images/hand.png'}),
      this.hand.cards.length]);

  info.children('.brain_damage').html([
      $('<img>', {src: '/static/images/brain.png'}), this.brainDamage]);
  info.children('.agendas').html([
      $('<img>', {src: '/static/images/chart.png'}),
      this.agendaPoints]);
  info.children('.tags').html([
      $('<img>', {src: '/static/images/crosshair.png'}), this.tags]);
  info.children('.link').html([
      $('<img>', {src: '/static/images/signal.png'}), this.link]);
  info.children('.memory').html([
      $('<img>', {src: '/static/images/memory.png'}), this.memory]);
  csrv.renderCardsInParent($('#runner_identity'), [this.identity]);
  this.renderHeap();
};

csrv.Runner.prototype.renderHosted = function() {
  for (var i = 0; i < this.rig.length; i++) {
    this.rig[i].renderHosted();
  }
};

csrv.Runner.prototype.renderHeap = function() {
  if (!this.heapDiv) {
    this.heapDiv = $('#heap');

    this.heapDiv.click(function() {
      console.log('clicked heap');
      var browser = new csrv.CardBrowser();
      browser.show({
        message: 'Heap',
        cards: csrv.game.runner.heap
      });
    });
  }

  if (this.heap.length) {
    var topCard = this.heap.slice(this.heap.length - 1)[0];
    this.heapDiv.empty();
    this.heapDiv.append(topCard.buildDiv());
  } else {
    this.heapDiv.empty();
    this.heapDiv.append($('<img>', {
      src: '/static/images/corp-empty.jpg',
      'class': 'placeholder'
    }));
  }
};

csrv.Server = function(options) {
  options = $.extend({
    serverType: 'remote'
  }, options || {});
  this.cards = [];
  this.ice = [];
  this.identity = null;
  this.installed = [];
  this.serverType = options['serverType'];
  this.serverState = null;
  this.gameId = null;
  this.div = null;
  this.runmeDiv = null;
  this.iceDiv = null;
  this.installedDiv = null;
  this.cardsDiv = null;
  this.activeRun = false;
  this.beingAccessed = false;
  this.choices = [];
};

csrv.Server.prototype.update = function(serverState, identity) {
  this.gameId = serverState['game_id'];
  csrv.gameRegistry[this.gameId] = this;
  this.name = serverState['name'];

  if (this.serverType != 'hq') {
    this.cards = csrv.updateCardArray(this, this.cards, serverState['cards']);
  }
  this.ice = csrv.updateCardArray(this, this.ice, serverState['ice']);
  this.installed = csrv.updateCardArray(
      this, this.installed, serverState['installed']);
  if (identity && !this.identity) {
    this.identity = new csrv.Card();
    this.identity.update(identity);
  }
};

csrv.Server.prototype.addChoice = function(choice) {
  this.choices.push(choice);
};

csrv.Server.prototype.removeChoice = function(choice) {
  this.choices.splice(this.choices.indexOf(choice), 1);
};

csrv.Server.prototype.render = function() {
  if (!this.div) {
    this.div = $('<div>', {'class': 'server'});
    /* todo reverse for runner */
    csrv.addToDivReverse($('#servers'), this.div);
  }
  if (!this.runmeDiv) {
    this.runmeDiv = $('<div>', {'class': 'runme'});
    this.runmeDiv.append($('<img>', {src: '/static/images/run.png'}));
    csrv.addToDiv(this.div, this.runmeDiv);
  }

  if (this.choices.length) {
    this.runmeDiv.show('fold');
    this.runmeDiv.attr('title', 'Make a run on ' + this.name);
    this.runmeDiv.unbind('dblclick');
    this.runmeDiv.dblclick(function(div, choice) {
      return function() {
        div.hide('explode');
        choice.resolve();
        div.unbind('dblclick');
      };
    }(this.runmeDiv, this.choices[0]));
  } else {
    this.runmeDiv.unbind('dblclick');
    this.runmeDiv.hide('fold');
    this.runmeDiv.attr('title', null);
  }
  if (this.activeRun) {
    this.div.addClass('run');
  } else {
    this.div.removeClass('run');
  }
  if (!this.iceDiv) {
    this.iceDiv = $('<div>', {'class': 'server_ice'});
    csrv.addToDiv(this.div, this.iceDiv);
  }
  if (!this.installedDiv) {
    this.installedDiv = $('<div>', {'class': 'server_installed'});
    csrv.addToDiv(this.div, this.installedDiv);
  }
  this.ice.reverse();
  csrv.renderCardsInParent(this.iceDiv, this.ice);
  csrv.renderCardsInParent(this.installedDiv, this.installed);
  if (!this.installed.length) {
    this.installedDiv.empty();
    csrv.addToDiv(this.installedDiv, $('<img>', {
      src: '/static/images/transparent.gif',
      'class': 'placeholder',
    }));
  }
  switch (this.serverType) {
    case 'archives':
      this.renderArchives();
      break;
    case 'hq':
      this.renderHq();
      break;
    case 'rnd':
      this.renderRnd();
      break;
    default:
      this.renderRemote();
  }
};

csrv.Server.prototype.renderHosted = function() {
  var sections = [this.ice, this.installed, this.cards];

  for (var i = 0; i < 3; i++) {
    section = sections[i];
    for (var c = 0; c < section.length; c++) {
      section[c].renderHosted();
    }
  }
};

csrv.Server.prototype.renderArchives = function() {
  if (!this.cardsDiv) {
    this.cardsDiv = $('<div>', {'class': 'corp_static'});
    this.installedDiv.before(this.cardsDiv);
    self = this;
    this.cardsDiv.click(function() {
      var browser = new csrv.CardBrowser();
      browser.show({
        message: 'Archives',
        cards: csrv.game.corp.archives.cards,
      });
    });
  }
  if (this.cards.length) {
    var topCard = this.cards.slice(this.cards.length - 1)[0];
    this.cardsDiv.empty();
    this.cardsDiv.append(topCard.buildDiv());
  } else {
    this.cardsDiv.empty();
    this.cardsDiv.append($('<img>', {src: '/static/images/corp-empty.jpg'}));
  }

  var accessDiv = $('#archives_access');
  if (this.beingAccessed) {
    csrv.renderCardsInParent(accessDiv, this.cards);
    var buttonOpts = {
      text: 'Auto-access remaining cards',
      click: function() {
        csrv.game.choices.autoAccess = true;
        csrv.game.choices.allChoices[0].resolve();
      }
    };
    accessDiv.dialog({
      title: 'Accessing Archives',
      dialogClass: 'no-close',
      buttons: [buttonOpts],
    });
    accessDiv.dialog('open');
  } else {
    for (var i = 0; i < this.cards.length; i++) {
      this.cards[i].unrender();
    }
    try {
      accessDiv.dialog('close');
    } catch(err) {
      accessDiv.hide();
    }
  }
};


csrv.Server.prototype.renderRnd = function() {
  if (!this.cardsDiv) {
    this.cardsDiv = $('<div>', {'class': 'corp_static'});
    this.installedDiv.before(this.cardsDiv);
  }
  if (this.cards.length) {
    this.cardsDiv.empty();
    this.cardsDiv.append($('<img>', {src: '/static/images/corp-back.jpg'}));
  } else {
    this.cardsDiv.empty();
    this.cardsDiv.append($('<img>', {src: '/static/images/corp-empty.jpg'}));
  }

};


csrv.Server.prototype.renderHq = function() {
  if (!this.cardsDiv) {
    this.cardsDiv = $('<div>', {'class': 'corp_static'});
    this.installedDiv.before(this.cardsDiv);
    this.identity.render();
    this.cardsDiv.append(this.identity.div);
  }

};

csrv.Server.prototype.renderRemote = function() {
  if (!this.cardsDiv) {
    this.cardsDiv = $('<div>', {'class': 'no_root'});
    csrv.addToDiv(this.cardsDiv, $('<img>', {
      src: '/static/images/transparent.gif',
      'class': 'placeholder'
    }));
    csrv.addToDiv(this.div, this.cardsDiv);
  }
};

csrv.CorpHand = function() {
  this.cards = null;
  var cardsDiv = $('#corp_hud #hand')[0];
  if (cardsDiv) {
    this.cardsDiv = $(cardsDiv);
  }
};

csrv.CorpHand.prototype.update = function(cards) {
  this.cards = csrv.updateCardArray(this, this.cards, cards);
};

csrv.CorpHand.prototype.render = function() {
  if (this.cardsDiv) {
    csrv.renderCardsInParent(this.cardsDiv, this.cards);
  }
};

csrv.RunnerHand = function() {
  this.cards = null;
  var cardsDiv = $('#runner_hud #hand')[0];
  if (cardsDiv) {
    this.cardsDiv = $(cardsDiv);
  }
};

csrv.RunnerHand.prototype.update = function(cards) {
  this.cards = csrv.updateCardArray(this, this.cards, cards);
};

csrv.RunnerHand.prototype.render = function() {
  if (this.cardsDiv) {
    csrv.renderCardsInParent(this.cardsDiv, this.cards);
  }
};
