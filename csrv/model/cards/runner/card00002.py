from csrv.model import actions
from csrv.model import cost
from csrv.model import errors
from csrv.model import parameters
from csrv.model.cards import card_info
from csrv.model.cards import event


class Card00002Action(actions.PlayEventAction):
  REQUEST_CLASS = parameters.HeapCardsRequest

  def is_usable(self):
    return bool(
        actions.PlayEventAction.is_usable(self) and self.player.heap.size)

  def resolve(self, response=None, ignore_clicks=False, ignore_all_costs=False):
    for card in response.cards:
      if not card.location == self.player.heap:
        raise errors.InvalidResponse(
            'You must select cards from the heap')
    if len(response.cards) == 2:
      for card in response.cards:
        if card_info.VIRUS not in response.cards[0].KEYWORDS:
          raise errors.InvalidResponse(
              'If you select two cards, they must both be viruses')
    elif len(response.cards) != 1:
      raise errors.InvalidResponse(
          'You must select either one card, or two virus cards')
    actions.PlayEventAction.resolve(
        self, response, ignore_clicks=ignore_clicks,
        ignore_all_costs=ignore_all_costs)
    for card in response.cards:
      self.player.grip.add(card)


class Card00002(event.Event):

  NAME = u'Card00002'
  SET = card_info.CORE
  NUMBER = 2
  SIDE = card_info.RUNNER
  FACTION = card_info.ANARCH
  INFLUENCE = 2
  UNIQUE = False
  COST = 2
  IMAGE_SRC = '01002.png'

  def build_actions(self):
    event.Event.build_actions(self)
    self._play_event_action = Card00002Action(self.game, self.player, self)

