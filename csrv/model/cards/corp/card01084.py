from csrv.model.cards import card_info
from csrv.model.cards import operation


class Card01084(operation.Operation):

  NAME = u'Card01084'
  SET = card_info.CORE
  NUMBER = 84
  SIDE = card_info.CORP
  FACTION = card_info.NEWSCORP
  INFLUENCE = 1
  UNIQUE = False
  KEYWORDS = set([
      card_info.GRAY_OPS,
  ])
  COST = 1
  IMAGE_SRC = '01084.png'

  def is_playable(self):
    return bool(operation.Operation.is_playable(self) and
                self.game.runner.tags)

  def play(self):
    self.game.runner.credits.set(0)
