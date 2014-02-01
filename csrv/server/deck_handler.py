import tornado.web
from csrv.model import read_o8d
from csrv.model import game
from csrv.model import deck
from csrv.server import data
from csrv.model import premade_decks


class DeckHandler(tornado.web.RequestHandler):
  def get(self, game_id, side):
    assert(data.Data.get(game_id))
    if side == 'corp':
      self.render('corp_deck.html', game_id=game_id, side=side,
                  decks=premade_decks.corp_decks)
    elif side == 'runner':
      self.render('runner_deck.html', game_id=game_id, side=side,
                  decks=premade_decks.runner_decks)

  def post(self, game_id, side):
    game_data = data.Data.get(game_id)
    assert(game_data)

    deck_file = self.request.files.get('file')
    if deck_file:
      decklist = read_o8d.read(deck_file[0]['body'])
    elif self.get_argument('premade'):
      if side == 'corp':
        premade = premade_decks.corp_decks[int(self.get_argument('premade'))]
      else:
        premade = premade_decks.runner_decks[int(self.get_argument('premade'))]
      decklist = [premade['identity'], premade['cards']]

    if side == 'corp':
      game_data.corp_deck = deck.CorpDeck(*decklist)
    else:
      game_data.runner_deck = deck.RunnerDeck(*decklist)
    if game_data.corp_deck and game_data.runner_deck:
      game_data.game = game.Game(game_data.corp_deck, game_data.runner_deck)
    self.redirect('/game/%s/%s/wait' % (game_id, side))
