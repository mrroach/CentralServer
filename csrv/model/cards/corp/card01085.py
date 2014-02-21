from csrv.model import actions
from csrv.model import errors
from csrv.model import parameters
from csrv.model import timing_phases
from csrv.model.cards import card_info
from csrv.model.cards import operation


class RearrangeCards(actions.Action):
  DESCRIPTION = 'Look at and rearrange the top 5 cards of R&D'

  def request(self):
    cards = self.game.corp.rnd.cards[-5:]
    return parameters.ArrangeCardsRequest(self.game, cards)

  def resolve(self, response=None, ignore_clicks=False, ignore_all_costs=False):
    if not response or not response.cards or not len(response.cards) == 5:
      raise errors.InvalidResponse(
          'You must arrange the top 5 cards of R&D')
    cards = self.game.corp.rnd.cards[-5:]
    if not set(cards) == set(response.cards):
      raise errors.InvalidResponse(
          'Selected cards are not from R&D')
    actions.Action.resolve(
        self, response,
        ignore_clicks=ignore_clicks,
        ignore_all_costs=False)
    for card in reversed(response.cards):
      self.game.corp.rnd.remove(card)
      self.game.corp.rnd.add(card)


class RearrangeCardsPhase(timing_phases.BasePhase):
  """Look at the top 5 cards of R&D and rearrange them."""
  NULL_OK = False

  def choices(self, refresh=False):
    if not self._choices or refresh:
      self._choices = [RearrangeCards(self.game, self.player)]
    return self._choices


class Card01085(operation.Operation):

  NAME = u'Card01085'
  SET = card_info.CORE
  NUMBER = 85
  SIDE = card_info.CORP
  FACTION = card_info.NEWSCORP
  INFLUENCE = 3
  UNIQUE = False
  COST = 0
  IMAGE_SRC = '01085.png'

  def build_actions(self):
    operation.Operation.build_actions(self)

  def play(self):
    operation.Operation.play(self)
    self.game.insert_next_phase(RearrangeCardsPhase(self.game, self.player))
