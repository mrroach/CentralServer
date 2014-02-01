/**
 * A server class to display both central and remote servers.
 */

csrv.ServerTypeEnum = {
  ARCHIVES: 0,
  HQ: 1,
  RND: 2,
  REMOTE: 3,
}

csrv.Server = function(gameId, attrs, serverType) {
  this.gameId = gameId;
  this.attrs = attrs;
  this.div = null;
  this.iceDiv = null;
  this.installedDiv = null;
  this.serverType = serverType || csrv.ServerTypeEnum.REMOTE;
  this.ice = [];
  this.installed = [];
  this.cards = [];  // centrals only
}

/**
 * Update the card divs with the info from serverDef (a gameState server hash).
 **/
csrv.Server.prototype.updateCards = function(serverDef) {

}

csrv.Server.prototype.addDiv = function() {
  this.div = $('<div>', {'class': 'server', 'id': this.gameId});
  this.iceDiv = $('<div>', {'class': 'server_ice'});
  this.installedDiv = $('<div>', {'class': 'server_installed'});
  this.div.append(this.iceDiv);
  this.div.append(this.installedDiv);
  $('#servers').prepend(this.div);

  switch (this.serverType) {
    case csrv.ServerTypeEnum.ARCHIVES:
      this.addArchivesDiv();
      break;
    case csrv.ServerTypeEnum.HQ:
      this.addHqDiv();
      break;
    case csrv.ServerTypeEnum.RND:
      this.addRndDiv();
      break;
  }
}

csrv.Server.prototype.addHqDiv = function() {
  csrv.rezzedCardDiv(
      corp['identity'], 'corp').insertBefore('.hq .server_installed');
}

csrv.Server.prototype.addRndDiv = function() {
  var rndDiv = $('<div>', {'class': 'corp_card'});
  rndDiv.append($('<img>', {'src': 'images/corp-back.jpg'}));
  this.installedDiv.before(rndDiv);
}

csrv.Server.prototype.addArchivesDiv = function() {
  if (corp['archives']['cards'].length) {
    var i = corp['archives']['cards'].length - 1;
    var card = corp['archives']['cards'][i];
    csrv.cardDiv(card, 'corp').insertBefore('.archives .server_installed');
  } else {
    var archivesDiv = $('<div>', {'class': 'corp_static'});
    archivesDiv.append($('<img>', {'src': 'images/corp-empty.jpg'}));
    archivesDiv.insertBefore('.archives .server_installed');
  } 
}

csrv.Server.prototype.remove = function() {
  this.div.remove();
}

