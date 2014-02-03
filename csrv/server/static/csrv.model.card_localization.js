csrv.CardLocalization = function() {
  this.uri = null;
  this.loaded = null;
  this.cards = {};
}

csrv.CardLocalization.prototype.loadFile = function(uri) {
  var self = this;
  $.getJSON(uri, function(data) {
    self.uri = uri;
    self.loaded = true;
    self.cards = data;
  });
}
