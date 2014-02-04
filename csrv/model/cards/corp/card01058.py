from csrv.model import actions
from csrv.model import errors
from csrv.model import parameters
from csrv.model.cards import card_info
from csrv.model.cards import operation


class Card01058Action(actions.PlayOperationAction):
  REQUEST_CLASS = parameters.ArchivesCardsRequest

  def is_usable(self):
    return bool(
        actions.PlayOperationAction.is_usable(self) and
        self.player.archives.size)

  def resolve(self, response, ignore_clicks=False, ignore_all_costs=False):
    for card in response.cards:
      if not card.location == self.player.archives:
        raise errors.InvalidResponse(
            'You must select a card from archives.')
    if len(response.cards) != 1:
      raise errors.InvalidResponse(
          'You must select exactly one card.')
    actions.PlayOperationAction.resolve(
        self, response,
        ignore_clicks=ignore_clicks,
        ignore_all_costs=ignore_all_costs)
    self.player.hq.add(response.cards[0])


class Card01058(operation.Operation):

  NAME = u'Card01058'
  SET = card_info.CORE
  NUMBER = 58
  SIDE = card_info.CORP
  FACTION = card_info.ROBOCORP
  INFLUENCE = 2
  UNIQUE = False
  COST = 0
  IMAGE_SRC = '01058.png'

  def build_actions(self):
    operation.Operation.build_actions(self)
    self._play_operation_action = Card01058Action(
        self.game, self.player, self)
