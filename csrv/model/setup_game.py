"""A module for interactive testing.

Use:
  $ python
  >>> from csrv.model import setup_game
  >>> setup_game.play()

this will prompt you for responses to choices if you break out at any point you
can access the game object as 'setup_game.g' and can resume the interactive
play with setup_game.play(setup_game.g)

"""

from csrv.model import game
from csrv.model import deck
from csrv.model import errors
from csrv.model import parameters
from csrv.model import premade_decks
from csrv.model import json_serializer
from csrv.model import read_o8d


def new_game(corp_deck_file=None, runner_deck_file=None):
  if corp_deck_file:
    corp_deck = deck.CorpDeck(*read_o8d.read_file(corp_deck_file))
  else:
    corp_deck = deck.CorpDeck(
      premade_decks.corp_decks[0]['identity'],
      premade_decks.corp_decks[0]['cards'])
  if runner_deck_file:
    runner_deck = deck.CorpDeck(*read_o8d.read_file(runner_deck_file))
  else:
    runner_deck = deck.RunnerDeck(
      premade_decks.runner_decks[0]['identity'],
      premade_decks.runner_decks[0]['cards'])
  return game.Game(corp_deck, runner_deck)


g = None

def play(game_obj=None):
  global g
  if game_obj:
    g = game_obj
  else:
    g = new_game()
  g.current_phase()
  while True:
    try:
      phase = g.current_phase()
      with open('game_state.json', 'w') as json_out:
        json_out.write(json_serializer.serialize_game_corp(g))

      player = phase.player
      if player == g.corp:
        hand = g.corp.hq
      else:
        hand = g.runner.grip
      choices = phase.choices()
      if choices:
        for i, choice in enumerate(choices):
          print '%d) %s  <%s>' % (i, choice, choice.cost)
        print '\n%s has %d credits, %d cards in hand, %d agenda points, %d clicks' % (
            player, player.credits.value, hand.size, player.agenda_points, player.clicks.value)
        chosen = raw_input('(%s) %s\'s Choice? : ' % (phase, player))
        if chosen:
          choice = choices[int(chosen)]
          req = choice.request()
          if (isinstance(req, parameters.InstallIceRequest) or
              isinstance(req, parameters.InstallAgendaAssetRequest) or
              isinstance(req, parameters.InstallUpgradeRequest)):
            resp = req.new_response()
            if isinstance(req, parameters.InstallAgendaAssetRequest):
              servers = g.corp.remotes
            else:
              servers = (
                  [g.corp.archives, g.corp.rnd, g.corp.hq] + g.corp.remotes)
            for x, server in enumerate(servers):
              print '%d) %s' % (x, server)
            server_choice = raw_input('Install in which server?: ')
            if server_choice:
              resp.server = servers[int(server_choice)]
            g.resolve_current_phase(choice, resp)
          else:
            g.resolve_current_phase(choices[int(chosen)], None)
        else:
          try:
            g.resolve_current_phase(None, None)
          except errors.ChoiceRequiredError:
            print 'You must choose one of the options.'
            continue
      else:
        g.resolve_current_phase(None, None)
    except errors.CostNotSatisfied, err:
      print '\033[31m%s\033[37m' % err
