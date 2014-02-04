from csrv.model import actions
from csrv.model import timing_phases
from csrv.model.cards import card_info
from csrv.model.cards import resource


class TrashCard(actions.Trash):
  DESCRIPTION = 'Trash a card to gain 3[Credits]'

  def __init__(self, game, player, card=None, card01047=None):
    actions.Trash.__init__(self, game, player, card=card)
    self.card01047 = card01047

  def resolve(self, response=None, ignore_clicks=False, ignore_all_costs=False):
    actions.Trash.resolve(
        self, response,
        ignore_clicks=ignore_clicks,
        ignore_all_costs=ignore_all_costs)
    self.player.credits.gain(3)
    self.card01047.used()

  @property
  def description(self):
    return 'Trash %s to gain 3 credits' % self.card


class Card01047(resource.Resource):

  NAME = u"Card01047"
  SET = card_info.CORE
  NUMBER = 47
  SIDE = card_info.RUNNER
  FACTION = card_info.SHAPER
  INFLUENCE = 2
  UNIQUE = True
  KEYWORDS = set([
      card_info.CONNECTION,
      card_info.LOCATION,
  ])
  COST = 1
  IMAGE_SRC = '01047.png'

  WHEN_INSTALLED_PROVIDES_CHOICES_FOR = {
      timing_phases.RunnerTurnBegin: 'trash_a_card',
  }

  def __init__(self, game, player):
    resource.Resource.__init__(self, game, player)
    self._used_on_turn = -1

  def build_actions(self):
    resource.Resource.build_actions(self)

  def trash_a_card(self):
    trash_actions = []
    if self._used_on_turn != self.game.runner_turn_count:
      for card in self.player.rig.cards:
        if not card == self:
          trash_actions.append(TrashCard(
              self.game, self.player, card=card, card01047=self))
    return trash_actions

  def used(self):
    self._used_on_turn = self.game.runner_turn_count
