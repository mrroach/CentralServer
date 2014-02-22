from csrv.model import events
from csrv.model import timing_phases
from csrv.model.cards import card_info
from csrv.model.cards import operation


class Card01072(operation.Operation):

  NAME = u'Card01072'
  SET = card_info.CORE
  NUMBER = 72
  SIDE = card_info.CORP
  FACTION = card_info.NETCORP
  INFLUENCE = 2
  UNIQUE = False
  KEYWORDS = set([
      card_info.GRAY_OPS,
  ])
  COST = 2
  IMAGE_SRC = '01072.png'
  LISTENS = [
      events.RunBegins
  ]

  def __init__(self, game, player):
    operation.Operation.__init__(self, game, player)
    self.last_run_made_turn = -1

  def build_actions(self):
    operation.Operation.build_actions(self)

  def play(self):
    self.game.insert_next_phase(
        timing_phases.TakeNetDamage(self.game, self.game.runner, 1))
    self.game.current_phase().begin()

  def on_run_begins(self, sender, event):
    self.last_run_made_turn = self.game.corp_turn_count

  def is_playable(self):
    return (operation.Operation.is_playable(self) and
            self.last_run_made_turn == self.game.corp_turn_count - 1)
