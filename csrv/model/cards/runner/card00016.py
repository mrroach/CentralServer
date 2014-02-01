from csrv.model import actions
from csrv.model import timing_phases
from csrv.model.cards import card_info
from csrv.model.cards import resource


class Card00016Action(actions.Action):

  DESCRIPTION = 'draw 2 cards and lose [Click].'
  def __init__(self, game, player, card):
    actions.Action.__init__(self, game, player, card=card)
    self._is_mandatory = True
    self._used_on_turn = None

  def is_usable(self):
    return (self.card.is_installed and
            self._used_on_turn != self.game.runner_turn_count)

  def resolve(self, response=None, ignore_clicks=False, ignore_all_costs=False):
    self._used_on_turn = self.game.runner_turn_count
    self.card.card00016()


class Card00016(resource.Resource):

  NAME = u'Card00016'
  SET = card_info.CORE
  NUMBER = 16
  SIDE = card_info.RUNNER
  FACTION = card_info.ANARCH
  INFLUENCE = 3
  UNIQUE = True
  KEYWORDS = set([
      card_info.LOCATION,
      card_info.SEEDY,
  ])
  COST = 3
  IMAGE_SRC = '01016.png'
  WHEN_INSTALLED_PROVIDES_CHOICES_FOR = {
      timing_phases.RunnerTurnBegin: 'card00016_actions',
  }

  def build_actions(self):
    resource.Resource.build_actions(self)
    self._card00016_action = Card00016Action(self.game, self.player, self)

  def card00016_actions(self):
    return [self._card00016_action]

  def card00016(self):
    self.game.runner.clicks.lose(1)
    for i in range(2):
      if self.game.runner.stack.cards:
        self.game.runner.grip.add(self.game.runner.stack.pop())

