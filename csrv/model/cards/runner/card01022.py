from csrv.model import actions
from csrv.model import errors
from csrv.model import parameters
from csrv.model.cards import card_info
from csrv.model.cards import event


class Card01022Action(actions.PlayEventAction):
  REQUEST_CLASS = parameters.StackCardRequest

  def is_usable(self):
    return bool(
        actions.PlayEventAction.is_usable(self) and self.player.stack.size)

  def resolve(self, response=None, ignore_clicks=False, ignore_all_costs=False):
    if (not response or not response.card or
        not response.card.location == self.player.stack):
          raise errors.InvalidResponse(
              'You must select a card from the stack')
    elif card_info.ICEBREAKER not in response.card.KEYWORDS:
      raise errors.InvalidResponse(
          'You must select an icebreaker')
    actions.PlayEventAction.resolve(
        self, response, ignore_clicks=ignore_clicks,
        ignore_all_costs=ignore_all_costs)
    self.player.grip.add(response.card)
    self.player.stack.shuffle()


class Card01022(event.Event):

  NAME = u'Card01022'
  SET = card_info.CORE
  NUMBER = 22
  SIDE = card_info.RUNNER
  FACTION = card_info.CRIMINAL
  INFLUENCE = 2
  UNIQUE = False
  COST = 1
  IMAGE_SRC = '01022.png'

  def build_actions(self):
    event.Event.build_actions(self)
    self._play_event_action = Card01022Action(self.game, self.player, self)
