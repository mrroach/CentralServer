csrv.setDefaultChoiceTimer = function() {
  if (csrv.defaultChoiceTimer) {
    csrv.clearDefaultChoice();
  }
  csrv.defaultChoiceTimer = setTimeout(function() {
    $('#choices').empty();
    $('#choices').append($('<h3>', {text: 'Nothing to do. passing'}));
    csrv.sendChoice(null) }, 2000);
};

csrv.Choices = function(game) {
  this.game = game;
  this.phase = null;
  this.nullOk = null;
  this.cardChoices = [];
  this.serverChoices = [];
  this.globalChoices = [];
  this.allChoices = [];
  this.fastMode = true;
  this.setupFastMode();
};

csrv.Choices.prototype.setupFastMode = function() {
  var self = this;
  $('body').keyup(function(event){
    /* catch spacebar */
    if (event.keyCode == 32){
      self.fastMode = !self.fastMode;
      if (self.fastMode) {
        self.fastModeEnable();
      } else {
        self.fastModeDisable();
      }
    }
  });
};

csrv.Choices.prototype.fastModeEnable = function() {
  this.fastMode = true;
  $('#fastmode').show('fade');
};

csrv.Choices.prototype.fastModeDisable = function() {
  this.fastMode = false;
  $('#fastmode').hide('fade');
};

csrv.Choices.prototype.update = function(choices) {
  this.phase = choices['phase'];
  this.description = choices['description'];
  this.player = choices['player'];
  this.nullOk = choices['null_ok'];
  this.nullChoice = choices['null_choice'];

  for (var i = 0; i < this.allChoices.length; i++) {
    this.allChoices[i].remove();
  }
  this.globalChoices = [];
  this.serverChoices = [];
  this.cardChoices = [];
  this.allChoices = [];

  if (this.isAccessPhase()) {
    this.setServerAccess();
  }

  if (!('choices' in choices)) {
    console.log('got no choices for ' + this.phase);
    console.log('player: ' + this.player);
    console.log(csrv.gameState);
    return;
  }

  for (var i = 0; i < choices['choices'].length; i++) {
    var choice = new csrv.Choice(i, choices['choices'][i]);
    if (choice.card) {
      this.cardChoices.push(choice);
    } else if (choice.server && choice.isRun()) {
      this.serverChoices.push(choice);
    } else {
      this.globalChoices.push(choice);
    }
    this.allChoices.push(choice);
    if (choice.type == 'ScoreAgenda') {
      /* Really don't want to screw people out of scoring agendas */
      this.fastModeDisable();
    }
  }
};

/**
 * Automatically resolve a timing phase either because there's nothing to do
 * or because the user has requested it.
 *
 * Return true if automatic actions were taken, false otherwise.
 */
csrv.Choices.prototype.handleAutoActions = function() {
  if (csrv.side != this.player) {
    return;
  }
  if (this.autoAccess) {
    if (this.phase != 'ApproachServer_4_5' && this.phase != 'AccessCard') {
      this.autoAccess = false;
    } else {
      if (this.allChoices.length) {
        this.allChoices[0].resolve();
        return true;
      } else {
        csrv.sendChoice(null);
        return true;
      }
    }
  }

  /* if there's only a single mandatory thing to do, do it. */
  if (this.allChoices.length == 1 && this.allChoices[0].isMandatory &&
      this.allChoices[0].request == 'NullRequest') {
    this.allChoices[0].resolve();
    return true;
  }

  if (this.fastMode) {
    /* Give the player a little bit of notice when their opponent's turn ends */
    if (csrv.game.run.server ||
      (csrv.game.corp.clicks == 0 && csrv.game.runner.clicks == 0)) {
    }
    if (this.phase == 'RunnerTurnAbilities' ||
        this.phase == 'CorpTurnAbilities' ||
        this.phase == 'ApproachServer_4_1' ||
        this.phase == 'ApproachServer_4_3') {
      $('#choices').empty();
      $('#choices').append($('<h3>', {text: 'Skipping rez/abilities'}));
      csrv.sendChoice(null);
      return true;
    } else if (this.phase == 'AccessCard') {
      /* Runner won't have a chance to see the card if we skip */
      return false;
    } else if (this.allChoices.length == 0) {
      csrv.sendChoice(null);
      return true;
    };
  }
  return false;
}

csrv.Choices.prototype.render = function() {
  var choiceDiv = $('#choices');
  choiceDiv.empty();
  choiceDiv.append($('<h3>', {text: this.description.replace(/([A-Z])/g, ' $1')}));

  for (var i = 0; i < this.globalChoices.length; i++) {
    choiceDiv.append(this.globalChoices[i].asLink());
  }
  for (var i = 0; i < this.cardChoices.length; i++) {
    var choice = this.cardChoices[i];
    if (!choice.card || !choice.card.div) {
      choiceDiv.append(choice.asLink());
    }
  }

  if (!this.handleAutoActions()) {
    /* Use the slower option for resolving empty choices */
    if (this.nullOk) {
      var nullChoice = new csrv.Choice(null, {
        description: this.nullChoice,
        request: 'NullRequest',
        cost: null});
      choiceDiv.append(nullChoice.asLink());
      if (this.allChoices.length == 0) {
        console.log('default choice timer would have been called');
      }
    }
  }
  if (this.player != csrv.side) {
    choiceDiv.append($('<h3>').text('Waiting for other player...'));
  }
};

csrv.Choices.prototype.isAccessPhase = function() {
  return this.phase == 'ApproachServer_4_5';
};

csrv.Choices.prototype.setServerAccess = function() {
  this.game.run.setServerAccess();
};


csrv.Choice = function(index, choice) {
  this.index = index;
  this.type = choice['type'];
  this.description = choice['description'];
  this.request = choice['request'];
  this.cost = choice['cost'];
  this.isMandatory = choice['is_mandatory'];
  this.validResponseOptions = choice['valid_response_options'];
  if (choice['card']) {
    this.card = csrv.gameRegistry[choice['card']['game_id']];
    if (this.card) {
      this.card.addChoice(this);
    }
  } else {
    this.card = null;
  }
  if (choice['server'] && this.isRun()) {
    this.server = csrv.gameRegistry[choice['server']];
    if (this.server) {
      this.server.addChoice(this);
    }
  }
};

csrv.Choice.prototype.isRun = function() {
  return (this.type == 'MakeARunAction');
};

csrv.Choice.prototype.resolve = function() {
  self = this;
  csrv.handleChoice(self);
};

csrv.Choice.prototype.remove = function() {
  if (this.card) {
    this.card.removeChoice(this);
  } else if (this.server && this.isRun()) {
    this.server.removeChoice(this);
  }
};

csrv.Choice.prototype.descriptionHtml = function() {
  var html = this.description;
  if (this.description.match(/\[[cC]red(it)?(s)?\]/)) {
    var cred = $('<img>', {
      'class': 'credit',
      src: '/static/images/credit.png'});
    html = html.replace(/\[[cC]red(it)?(s)?\]/g, cred[0].outerHTML);
  }
  if (this.description.match(/\[[cC]lick\]/)) {
    var cred = $('<img>', {
      'class': 'click',
      src: '/static/images/click.png'});
    html = html.replace(/\[[cC]lick\]/g, cred[0].outerHTML);
  }
  if (md = this.description.match(/(Card\d{5})/)) {
    var cardName = csrv.game.localization.cards[md[1]];
    if (cardName) {
      html = html.replace(/Card\d{5}/g, cardName);
    }
  }

  return html
}

csrv.Choice.prototype.asLink = function() {
  var self = this;
  var choose = function(event) {
    csrv.clearDefaultChoice();
    var gameId = $(event.target).attr('value');
    csrv.handleChoice(self);
  };
  var link = $('<a>', {href: '#', html: this.descriptionHtml()});
  link.click(choose);
  return link;
};

csrv.Choice.prototype.asTableRow = function() {
  var self = this;
  var choose = function(event) {
    csrv.clearDefaultChoice();
    var gameId = $(event.target).attr('value');
    csrv.handleChoice(self);
  };
  var button = $('<button>',
      {type: 'button', value: this.index}).text('choose');
  button.click(choose);
  var row = $('<tr>').append(
      $('<td>').text(this.description),
      $('<td>').html(button)
  );
  return row;
};

/*
csrv.displayChoices = function(choices, textStatus, jqXHR) {
  csrv.currentChoices = choices;
  var choiceDiv = $('#choices');
  choiceDiv.empty();
  choiceDiv.append($('<h3>', {text: choices['phase']}));
  var table = $('<table>');
  table.appendTo(choiceDiv);
  if ('choices' in choices) {
    for (var i = 0; i < choices['choices'].length; i++) {
      if ('card' in choices['choices'][i] && choices['choices'][i]['card']) {
        var cardObj = csrv.gameRegistry[choices['choices'][i]['card']];
        if (cardObj) {
          cardObj.hilight();
        }
      }
      var button = $('<button>', {type: 'button', value: i}).text('choose');
      var choose = function(event) {
        csrv.clearDefaultChoice();
        var gameId =
          $(event.target).attr('value') || $(event.target).attr('id');
        csrv.handleChoice(+gameId);
      };
      var cardId = choices['choices']['card'];
      if (cardId) {
        var card = $('#' + cardId);
        card.dblclick(choose);
      }
      button.click(choose);
      var row = $('<tr>').append(
          $('<td>').text(choices['choices'][i]['description']),
          $('<td>').html(button)
      );
      row.appendTo(table);
    }
    var button = $('<button>', {type: 'button'}).text('choose');
    button.click(function(event) { csrv.sendChoice(null); });
    var row = $('<tr>').append(
        $('<td>').text('Do nothing'),
        $('<td>').html(button)
    );
    table.append(row);
    if (choices['choices'].length == 0) {
      csrv.setDefaultChoiceTimer();
    }
  } else {
    choiceDiv.append($('<h3>').text('Waiting for other player...'));
  }
};
*/

csrv.ChoiceHandler = function(choice, responseType) {
  this.choice = choice;
  this.choiceIndex = choice ? choice.index : null;
  this.responseType = responseType;

  this.hasServer = false;
  this.server = null;

  this.hasIceToTrash = false;
  this.iceToTrash = null;

  this.hasProgramsToTrash = false;
  this.programsToTrash = null;

  this.hasCardsToTrash = false;
  this.cardsToTrash = null;

  this.hasCard = false;
  this.card = null;

  this.hasHost = false;
  this.host = null;

  this.hasNumber = false;
  this.number = null;
};

csrv.ChoiceHandler.prototype.clearChoices = function() {
  $('#choices').empty();
};

csrv.ChoiceHandler.prototype.setServerChoice = function(server) {
  this.server = server;
  this.hasServer = true;
  this.checkResponse();
};

csrv.ChoiceHandler.prototype.showServerChoices = function(options) {
  options = $.extend({
    centrals: true,
    remotes: true,
    newRemote: true},
    options || {});

  var choiceDiv = $('#choices');
  choiceDiv.append($('<h3>', {text: 'Choose a server'}));
  var servers = [];
  if (options['centrals']) {
    servers = [
      csrv.gameState['corp']['archives'],
      csrv.gameState['corp']['hq'],
      csrv.gameState['corp']['rnd']
    ];
  }
  if (options['remotes']) {
    for (var i = 0; i < csrv.gameState['corp']['remotes'].length; i++) {
      servers.push(csrv.gameState['corp']['remotes'][i]);
    }
  }
  if (options['newRemote']) {
    servers.push({'game_id': null, 'name': 'New remote'});
  }
  for (var i = 0; i < servers.length; i++) {
    var self = this;
    var data = {serverId: servers[i]['game_id']};
    var choose = (
      function (serverId) {
        return function(event) {
          self.setServerChoice(serverId);
        }
      })(servers[i]['game_id']);
    var link = $('<a>', {href: '#', html: servers[i]['name']});
    link.click(choose);
    choiceDiv.append(link);
  }
};

csrv.InstallIceResponseHandler = function(choice) {
  csrv.ChoiceHandler.call(this, choice, 'InstallIceResponse');
  this.checkResponse();
};

csrv.InstallIceResponseHandler.prototype = new csrv.ChoiceHandler();
csrv.InstallIceResponseHandler.prototype.constructor =
    csrv.InstallIceResponseHandler;

csrv.InstallIceResponseHandler.prototype.checkResponse = function() {
  if (this.hasServer) {
    var response = {
      response_type: this.responseType,
      response_data: {
        server: this.server
      }
    };
    csrv.sendChoice(this.choiceIndex, response);
  } else {
    this.clearChoices();
    this.showServerChoices();
  }
};

csrv.InstallAgendaAssetResponseHandler = function(choice) {
  csrv.ChoiceHandler.call(this, choice, 'InstallAgendaAssetResponse');
  this.checkResponse();
};
csrv.InstallAgendaAssetResponseHandler.prototype = new csrv.ChoiceHandler();
csrv.InstallAgendaAssetResponseHandler.prototype.constructor =
    csrv.InstallAgendaAssetResponseHandler;

csrv.InstallAgendaAssetResponseHandler.prototype.checkResponse = function() {
  if (this.hasServer) {
    var response = {
      response_type: this.responseType,
      response_data: {
        server: this.server
      }
    };
    csrv.sendChoice(this.choiceIndex, response);
  } else {
    this.clearChoices();
    this.showServerChoices({centrals: false});
  }
};

csrv.InstallUpgradeResponseHandler = function(choice) {
  csrv.ChoiceHandler.call(this, choice, 'InstallUpgradeResponse');
  this.checkResponse();
};
csrv.InstallUpgradeResponseHandler.prototype = new csrv.ChoiceHandler();
csrv.InstallUpgradeResponseHandler.prototype.constructor =
    csrv.InstallUpgradeResponseHandler;

csrv.InstallUpgradeResponseHandler.prototype.checkResponse = function() {
  if (this.hasServer) {
    var response = {
      response_type: this.responseType,
      response_data: {
        server: this.server
      }
    };
    csrv.sendChoice(this.choiceIndex, response);
  } else {
    this.clearChoices();
    this.showServerChoices({centrals: true});
  }
};


csrv.InstallProgramResponseHandler = function(choice) {
  csrv.ChoiceHandler.call(this, choice, 'InstallProgramResponse');
  this.host = null;
  this.hasHost = false;
  this.hostChoices = [];

  this.toTrash = [];
  this.hasTrash = false;
  this.trashChoices = [];
  this.checkResponse();
};
csrv.InstallProgramResponseHandler.prototype = new csrv.ChoiceHandler();
csrv.InstallProgramResponseHandler.prototype.constructor =
    csrv.InstallProgramResponseHandler;

csrv.InstallProgramResponseHandler.prototype.checkResponse = function() {
  if (!this.hasHost) {
    if (this.choice.validResponseOptions['host'].length) {
      this.clearChoices();
      this.showHostChoices(this.choice.validResponseOptions['host']);
    } else {
      this.hasHost = true;
    }
  }
  if (this.hasHost && !this.hasTrash) {
    if (this.choice.validResponseOptions['programs_to_trash'].length) {
      this.clearChoices();
      this.showTrashChoices(
          this.choice.validResponseOptions['programs_to_trash']);
    } else {
      this.hasTrash = true;
    }
  }
  if (this.hasHost && this.hasTrash) {
    var response = {
      response_type: this.responseType,
      response_data: {
        host: this.host,
        programs_to_trash: this.toTrash
      }
    };
    csrv.sendChoice(this.choiceIndex, response);
  }
};

csrv.InstallProgramResponseHandler.prototype.showHostChoices = function(hosts) {
  var choiceDiv = $('#choices');
  var self = this;
  this.hostChoices = []
  csrv.destroyTooltip();
  for (var i = 0; i < hosts.length; i++) {
    var host = csrv.gameRegistry[hosts[i]];
    if (host) {
      var choice = new csrv.ResponseChoice(
          'Host on ' + host.name, this.setHostChoice.bind(this), hosts[i]);
      this.hostChoices.push(choice);
      host.clearChoices();
      host.addChoice(choice);
      host.render();
    }
  }
  csrv.createTooltip();

  choiceDiv.append($('<h3>', {text: 'Choose a host'}));
  var link = $('<a>', {href: '#', html: 'No host'});
  var choice = new csrv.ResponseChoice(
      'No host', this.setHostChoice.bind(this), null);
  link.click(function() { choice.resolve() });
  choiceDiv.append(link);
};

csrv.InstallProgramResponseHandler.prototype.showTrashChoices =
    function(targets) {
  var choiceDiv = $('#choices');
  csrv.destroyTooltip();
  /* need to give the option to unselect accidentally selected programs here **/
  /* also add a visual trash indicator to the selected card */
  for (var i = 0; i < targets.length; i++) {
    var target = csrv.gameRegistry[targets[i]];
    if (target) {
      var idx = this.toTrash.indexOf(targets[i]);
      if (idx == -1) {
        var message = 'Trash ' + target.name;
      } else {
        var message = 'Do not trash ' + target.name;
      }
      var choice = new csrv.ResponseChoice(
          message, this.addTrashChoice.bind(this), targets[i]);
      this.trashChoices.push(choice);
      target.clearChoices();
      target.addChoice(choice);
      target.render();
    }
  }
  csrv.createTooltip();
  choiceDiv.append($('<h3>', {text: 'Choose to trash programs'}));
  var link = $('<a>', {href: '#', html: 'Done trashing'});
  var self = this;
  var choice = new csrv.ResponseChoice(
      'Done trashing', this.addTrashChoice.bind(this), null);
  link.click(function() { choice.resolve(); });
  choiceDiv.append(link);
};

csrv.InstallProgramResponseHandler.prototype.addTrashChoice = function(cardId) {

  console.log('Setting hasTrash');
  if (!cardId) {
    this.hasTrash = true;
  } else {
    var target = csrv.gameRegistry[cardId];
    var idx = this.toTrash.indexOf(cardId);
    if (idx == -1) {
      target.addTrashIcon();
      this.toTrash.push(cardId);
    } else {
      target.removeTrashIcon();
      this.toTrash.splice(idx, 1);
    }
  }

  for (var i = 0; i < this.trashChoices.length; i++) {
    var choice = this.trashChoices[i];
    var card = csrv.gameRegistry[choice.value];
    if (card) {
      card.removeChoice(choice);
    }
  }
  this.checkResponse();
};

csrv.InstallProgramResponseHandler.prototype.setHostChoice = function(hostId) {
  this.hasHost = true;
  this.host = hostId;
  for (var i = 0; i < this.hostChoices.length; i++) {
    var choice = this.hostChoices[i];
    var host = csrv.gameRegistry[choice.value];
    if (host) {
      host.removeChoice(choice);
    }
  }
  this.checkResponse();
};

csrv.InstallHardwareResponseHandler = function(choice) {
  csrv.ChoiceHandler.call(this, choice, 'InstallHardwareResponse');
  this.host = null;
  this.hasHost = false;
  this.hostChoices = [];
  this.checkResponse();
};
csrv.InstallHardwareResponseHandler.prototype = new csrv.ChoiceHandler();
csrv.InstallHardwareResponseHandler.prototype.constructor =
    csrv.InstallHardwareResponseHandler;

csrv.InstallHardwareResponseHandler.prototype.showHostChoices = function(hosts) {
  var choiceDiv = $('#choices');
  var self = this;
  this.hostChoices = []
  csrv.destroyTooltip();
  for (var i = 0; i < hosts.length; i++) {
    var host = csrv.gameRegistry[hosts[i]];
    if (host) {
      var choice = new csrv.ResponseChoice(
          'Host on ' + host.name, this.setHostChoice.bind(this), hosts[i]);
      this.hostChoices.push(choice);
      host.clearChoices();
      host.addChoice(choice);
      host.render();
    }
  }
  csrv.createTooltip();

  choiceDiv.append($('<h3>', {text: 'Choose a host'}));
  var link = $('<a>', {href: '#', html: 'No host'});
  link.click(new csrv.ResponseChoice(self.setHostChoice, null));
  choiceDiv.append(link);
};

csrv.InstallHardwareResponseHandler.prototype.setHostChoice = function(hostId) {
  this.hasHost = true;
  this.host = hostId;
  for (var i = 0; i < this.hostChoices.length; i++) {
    var choice = this.hostChoices[i];
    var host = csrv.gameRegistry[choice.value];
    if (host) {
      host.removeChoice(choice);
    }
  }
  this.checkResponse();
};

csrv.InstallHardwareResponseHandler.prototype.checkResponse = function() {
  if (!this.hasHost) {
    if (this.choice.validResponseOptions['host'].length) {
      this.clearChoices();
      this.showHostChoices(this.choice.validResponseOptions['host']);
    } else {
      this.hasHost = true;
    }
  }
  if (this.hasHost) {
    var response = {
      response_type: this.responseType,
      response_data: {
        host: this.host
      }
    };
    csrv.sendChoice(this.choiceIndex, response);
  }
};


csrv.ResponseChoice = function(description, callback, value) {
  this.description = description;
  this.callback = callback;
  this.value = value;
};

csrv.ResponseChoice.prototype.descriptionHtml = function() {
  return this.description;
};

csrv.ResponseChoice.prototype.resolve = function() {
  this.callback(this.value);
};

csrv.VariableCreditCostResponseHandler = function(choice) {
  csrv.ChoiceHandler.call(this, choice, 'VariableCreditCostResponse');
  this.credits = 0;
  this.hasCredits = false;
  this.checkResponse();
};
csrv.VariableCreditCostResponseHandler.prototype = new csrv.ChoiceHandler();
csrv.VariableCreditCostResponseHandler.prototype.constructor =
    csrv.VariableCreditCostResponseHandler;

csrv.VariableCreditCostResponseHandler.prototype.checkResponse = function() {
  if (!this.hasCredits) {
    this.clearChoices();
    this.showCreditChoices();
  }
  if (this.hasCredits) {
    var response = {
      response_type: this.responseType,
      response_data: {
        credits: +this.credits
      }
    };
    csrv.sendChoice(this.choiceIndex, response);
  }
};

csrv.VariableCreditCostResponseHandler.prototype.setCreditChoice =
    function(value) {
  this.hasCredits = true;
  this.credits = value;
  this.checkResponse();
};

csrv.VariableCreditCostResponseHandler.prototype.showCreditChoices = function() {
  var div = $('<div>', {id: 'dialog', text: 'Choose an amount to spend '});
  $('body').append(div);
  var spinner = $('<input>', {
    type: 'number',
    value: this.credits,
    min: "0",
    name: 'credits'
  });
  var self = this;
  var choose = function () {
    return function(event) {
      var val = spinner.val();
      div.dialog('close');
      div.dialog('destroy');
      div.remove();
      self.setCreditChoice(spinner.val());
    }
  }();

  /*spinner.spinner({min: 0});*/
  div.append(spinner);
  div.dialog({
    modal: true,
    buttons: [{text: 'Ok', click: choose}]
  });
  div.dialog('open');
};

csrv.NumericChoiceResponseHandler = function(choice) {
  csrv.ChoiceHandler.call(this, choice, 'NumericChoiceResponse');
  this.message = choice.description;
  this.number = 0;
  this.hasNumber = false;
  this.checkResponse();
};

csrv.NumericChoiceResponseHandler.prototype = new csrv.ChoiceHandler();
csrv.NumericChoiceResponseHandler.prototype.constructor =
    csrv.NumericChoiceResponseHandler;

csrv.NumericChoiceResponseHandler.prototype.checkResponse = function() {
  if (!this.hasNumber) {
    this.clearChoices();
    this.showNumberChoices();
  }
  if (this.hasNumber) {
    var response = {
      response_type: this.responseType,
      response_data: {
        number: this.number
      }
    };
    csrv.sendChoice(this.choiceIndex, response);
  }
};

csrv.NumericChoiceResponseHandler.prototype.setNumberChoice =
    function(value) {
  this.hasNumber = true;
  this.number = +value;
  this.checkResponse();
};

csrv.NumericChoiceResponseHandler.prototype.showNumberChoices = function() {
  var div = $('<div>', {id: 'dialog', text: 'Choose a number '});
  $('body').append(div);
  var spinner = $('<input>', {
    type: 'number',
    value: this.number,
    min: "0",
    name: 'number'
  });
  var self = this;
  var choose = function () {
    return function(event) {
      var val = spinner.val();
      div.dialog('close');
      div.dialog('destroy');
      div.remove();
      self.setNumberChoice(spinner.val());
    }
  }();

  /*spinner.spinner({min: 0});*/
  div.append(spinner);
  div.dialog({
    modal: true,
    buttons: [{text: 'Ok', click: choose}],
    title: this.message
  });
  div.dialog('open');
};


csrv.SearchForCardsResponseHandler = function(choice, responseType) {
   csrv.ChoiceHandler.call(this, choice, responseType);
};
csrv.SearchForCardsResponseHandler.prototype = new csrv.ChoiceHandler();

csrv.SearchForCardsResponseHandler.prototype.checkResponse = function() {
  if (!this.hasCards) {
    this.clearChoices();
    this.showCardChoices();
  }
  if (this.hasCards) {
    if (this.num == 1) {
      var response_data = {card: this.cards[0]};
    } else {
      var response_data = {cards: this.cards};
    }
    var response = {
      response_type: this.responseType,
      response_data: response_data
    };
    csrv.sendChoice(this.choiceIndex, response);
  }
};

csrv.SearchForCardsResponseHandler.prototype.setCards = function(cards) {
  if (!this.num || (this.num == 1 && cards.length == 1)) {
    this.cards = cards || [];
    this.hasCards = true;
  }
  this.checkResponse();
};


csrv.SearchForCardsResponseHandler.prototype.showCardChoices = function() {
  var browser = new csrv.CardBrowser();
  browser.show({
    message: 'Choose cards',
    cards: this.cardChoices(),
    callback: this.setCards.bind(this)
  });
};

csrv.ArrangeCardsResponseHandler = function(choice, responseType) {
   csrv.ChoiceHandler.call(this, choice, 'ArrangeCardsResponse');
  this.checkResponse();
};
csrv.ArrangeCardsResponseHandler.prototype = new csrv.ChoiceHandler();
csrv.ArrangeCardsResponseHandler.prototype.constructor =
    csrv.ArrangeCardsResponseHandler;

csrv.ArrangeCardsResponseHandler.prototype.checkResponse = function() {
  if (!this.hasCards) {
    this.clearChoices();
    this.showCardChoices();
  }
  if (this.hasCards) {
    var response_data = {cards: this.cards};
    var response = {
      response_type: this.responseType,
      response_data: response_data
    };
    csrv.sendChoice(this.choiceIndex, response);
  }
};

csrv.ArrangeCardsResponseHandler.prototype.setCards = function(cards) {
  this.cards = cards;
  this.hasCards = true;
  this.checkResponse();
};

csrv.ArrangeCardsResponseHandler.prototype.showCardChoices = function() {
  var browser = new csrv.CardBrowser();
  browser.show({
    message: 'Arrange cards from top (left) to bottom (right)',
    cards: this.cardChoices(),
    callback: this.setCards.bind(this),
    allowSelect: false,
    sortable: true
  });
};

csrv.ArrangeCardsResponseHandler.prototype.cardChoices = function() {
  var cardIds = this.choice.validResponseOptions['cards'];
  var cards = [];
  for (var i = 0; i < cardIds.length; i++) {
    cards.push(csrv.gameRegistry[cardIds[i]]);
  }
  return cards;
};

csrv.ArchivesCardsResponseHandler = function(choice) {
  csrv.SearchForCardsResponseHandler.call(
      this, choice, 'ArchivesCardsResponse');
  this.message = choice ? choice.description : null;
  this.cards = [];
  this.hasCards = false;
  this.checkResponse();
};

csrv.ArchivesCardsResponseHandler.prototype =
    new csrv.SearchForCardsResponseHandler();
csrv.ArchivesCardsResponseHandler.prototype.constructor =
    csrv.ArchivesCardsResponseHandler;

csrv.ArchivesCardsResponseHandler.prototype.cardChoices = function() {
  return csrv.game.corp.archives.cards;
};

csrv.RndCardsResponseHandler = function(choice) {
  csrv.SearchForCardsResponseHandler.call(
      this, choice, 'RndCardsResponse');
  this.message = choice ? choice.description : null;
  this.cards = [];
  this.hasCards = false;
  this.checkResponse();
};

csrv.RndCardsResponseHandler.prototype =
    new csrv.SearchForCardsResponseHandler();
csrv.RndCardsResponseHandler.prototype.constructor =
    csrv.RndCardsResponseHandler;

csrv.RndCardsResponseHandler.prototype.cardChoices = function() {
  return csrv.game.corp.rnd.cards;
};

csrv.StackCardsResponseHandler = function(choice) {
  csrv.SearchForCardsResponseHandler.call(this, choice, 'StackCardResponse');
  this.message = choice.description;
  this.num = 1;
  this.cards = [];
  this.hasCards = false;
  this.checkResponse();
};

csrv.StackCardsResponseHandler.prototype =
  new csrv.SearchForCardsResponseHandler();
csrv.StackCardsResponseHandler.prototype.constructor =
    csrv.StackCardsResponseHandler;

csrv.StackCardsResponseHandler.prototype.cardChoices = function() {
  return csrv.game.runner.stack;
};

csrv.HeapCardsResponseHandler = function(choice) {
  csrv.SearchForCardsResponseHandler.call(
      this, choice, 'HeapCardsResponse');
  this.message = choice ? choice.description : null;
  this.cards = [];
  this.hasCards = false;
  this.checkResponse();
};

csrv.HeapCardsResponseHandler.prototype =
    new csrv.SearchForCardsResponseHandler();
csrv.HeapCardsResponseHandler.prototype.constructor =
    csrv.HeapCardsResponseHandler;

csrv.HeapCardsResponseHandler.prototype.cardChoices = function() {
  return csrv.game.runner.heap;
};


csrv.handleChoice = function(choice) {
  var response = null;
  switch (choice.request) {
    case 'NullRequest':
      break;
    case 'InstallProgramRequest':
      return new csrv.InstallProgramResponseHandler(choice);
      break;
    case 'InstallHardwareRequest':
      return new csrv.InstallHardwareResponseHandler(choice);
      break;
    case 'TargetServerRequest':
      response = {
        response_type: 'TargetServerResponse',
        response_data: {}
      };
      break;
    case 'InstallResourceRequest':
      response = {
        response_type: 'InstallResourceResponse',
        response_data: {}
      };
      break;
    case 'InstallIceRequest':
      return new csrv.InstallIceResponseHandler(choice);
      break;
    case 'VariableCreditCostRequest':
      return new csrv.VariableCreditCostResponseHandler(choice);
      break;
    case 'NumericChoiceRequest':
      return new csrv.NumericChoiceResponseHandler(choice);
      break;
    case 'InstallAgendaAssetRequest':
      return new csrv.InstallAgendaAssetResponseHandler(choice);
      break;
    case 'InstallUpgradeRequest':
      return new csrv.InstallUpgradeResponseHandler(choice);
      break;
    case 'ArchivesCardsRequest':
      return new csrv.ArchivesCardsResponseHandler(choice);
      break;
    case 'RndCardsRequest':
      return new csrv.RndCardsResponseHandler(choice);
      break;
    case 'StackCardRequest':
      return new csrv.StackCardsResponseHandler(choice);
      break;
    case 'HeapCardRequest':
      return new csrv.HeapCardsResponseHandler(choice);
      break;
    case 'ArrangeCardsRequest':
      return new csrv.ArrangeCardsResponseHandler(choice);
      break
  }
  console.log('choice of last resort');
  csrv.sendChoice(choice.index, response);
};

csrv.lastChoiceProvided = -1;

/*
 * Send a choice via websocket connection.
 */
csrv.sendChoice = function(index, response) {
  csrv.clearDefaultChoice();
  if (csrv.lastChoiceProvided >= csrv.game.choiceCount) {
    console.log('Tried to send multiple choices for one phase.');
    return;
  };
  csrv.lastChoiceProvided = csrv.game.choiceCount;
  console.log('Sending ' + index + ' for ' + csrv.game.choices.phase);
  if (!response) {
    var response = {
      'response_type': 'NullResponse',
      'response_data': {}
    };
  }
  var data = JSON.stringify({
    'index': index,
    'player': csrv.side,
    'choiceCount': csrv.game.choiceCount,
    'phase': csrv.game.choices.phase,
    'response': response
  });
  csrv.ws.send(data);
};
