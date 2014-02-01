from csrv.model import actions
from csrv.model import events
from csrv.model import parameters
from csrv.model.cards import card_info
from csrv.model.cards import operation


class Card00097Action(actions.PlayOperationAction):
  REQUEST_CLASS = parameters.RndCardsRequest

  def is_usable(self):
    return (
        actions.PlayOperationAction.is_usable(self) and
        self.agenda_scored_this_turn())

  def agenda_scored_this_turn(self):
    return self.card.last_agenda_scored_turn == self.game.corp_turn_count

  def resolve(self, response, ignore_clicks=False, ignore_all_costs=False):
    for card in response.cards:
      if not card.location == self.player.rnd:
        raise errors.InvalidResponse(
            'You must select a card from R&D.')
    if len(response.cards) != 1:
      raise errors.InvalidResponse(
          'You must select exactly one card.')
    actions.PlayOperationAction.resolve(
        self, response,
        ignore_clicks=ignore_clicks,
        ignore_all_costs=ignore_all_costs)
    self.player.hq.add(response.cards[0])
    self.player.rnd.shuffle()


class Card00097(operation.Operation):

  NAME = u'Card00097'
  SET = card_info.CORE
  NUMBER = 97
  SIDE = card_info.CORP
  FACTION = card_info.MEATCORP
  INFLUENCE = 1
  UNIQUE = False
  COST = 1
  IMAGE_SRC = '01097.png'

  LISTENS = [
      events.ScoreAgenda,
  ]

  def __init__(self, game, player):
    operation.Operation.__init__(self, game, player)
    self.last_agenda_scored_turn = -1

  def build_actions(self):
    operation.Operation.build_actions(self)
    self._play_operation_action = Card00097Action(
        self.game, self.player, self)

  def on_score_agenda(self, sender, event):
    self.last_agenda_scored_turn = self.game.corp_turn_count

