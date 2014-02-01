from csrv.model import trace
from csrv.model.cards import card_info
from csrv.model.cards import operation


class Card00086(operation.Operation):

  NAME = u'Card00086'
  SET = card_info.CORE
  NUMBER = 86
  SIDE = card_info.CORP
  FACTION = card_info.NEWSCORP
  INFLUENCE = 2
  UNIQUE = False
  COST = 2
  IMAGE_SRC = '01086.png'

  def build_actions(self):
    operation.Operation.build_actions(self)

  def play(self):
    trace.Trace(self.game, 3, self, 'on_success', 'on_failure')

  def on_success(self, corp_total, runner_total):
    self.log('The runner takes a tag')
    self.game.runner.tags += 1

  def on_failure(self, corp_total, runner_total):
    pass
