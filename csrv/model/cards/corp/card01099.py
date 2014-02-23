from csrv.model import timing_phases
from csrv.model.cards import card_info
from csrv.model.cards import operation


class Card01099(operation.Operation):

  NAME = u'Card01099'
  SET = card_info.CORE
  NUMBER = 99
  SIDE = card_info.CORP
  FACTION = card_info.MEATCORP
  INFLUENCE = 4
  UNIQUE = False
  KEYWORDS = set([
      card_info.BLACK_OPS,
  ])
  COST = 3
  IMAGE_SRC = '01099.png'

  def build_actions(self):
    operation.Operation.build_actions(self)

  def is_playable(self):
    return bool(operation.Operation.is_playable(self) and
                self.game.runner.tags)

  def play(self):
    self.game.insert_next_phase(
        timing_phases.TakeMeatDamage(self.game, self.game.runner, 4))
