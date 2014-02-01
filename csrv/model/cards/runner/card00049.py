from csrv.model import actions
from csrv.model.cards import card_info
from csrv.model.cards import event
from csrv.model import parameters


class GainCreditsAction(actions.PlayEventAction):
  def resolve(self, response=None, ignore_clicks=False, ignore_all_costs=False):
    actions.PlayEventAction.resolve(
        self, response, ignore_clicks=ignore_clicks,
        ignore_all_costs=ignore_all_costs)
    self.card.gain_credits()

  @property
  def description(self):
    return 'Play Card00049 for 2 [credits]'


class ExposeCardAction(actions.PlayEventAction):
  REQUEST_CLASS = parameters.TargetInstalledCorpCardRequest

  def resolve(self, response=None, ignore_clicks=False, ignore_all_costs=False):
    if (response and response.card and
        response.card.player == self.game.corp and
        response.card.is_installed):
      actions.PlayEventAction.resolve(
          self, response, ignore_clicks=ignore_clicks,
          ignore_all_costs=ignore_all_costs)
      self.card.expose(response.card)
    else:
      raise errors.InvalidResponse(
          'You must select an installed card belonging to the corp')

  @property
  def description(self):
    return 'Play Card00049 to expose a card'


class Card00049(event.Event):

  NAME = u'Card00049'
  SET = card_info.CORE
  NUMBER = 49
  SIDE = card_info.RUNNER
  FACTION = card_info.NEUTRAL
  INFLUENCE = 0
  UNIQUE = False
  COST = 0
  IMAGE_SRC = '01049.png'

  def build_actions(self):
    event.Event.build_actions(self)
    self._gain_credits_action = GainCreditsAction(self.game, self.player, self)
    self._expose_card_action = ExposeCardAction(self.game, self.player, self)

  def play_event_actions(self):
    return [
        self._gain_credits_action,
        self._expose_card_action,
    ]

  def gain_credits(self):
    self.game.runner.credits.gain(2)

  def expose(self, card):
    self.game.expose_card(card)
