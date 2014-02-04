from csrv.model import actions
from csrv.model import events
from csrv.model import modifiers
from csrv.model.cards import card_info
from csrv.model.cards import event


class Card01036RunAction(actions.PlayEventAction):

  def __init__(self, game, player, card=None):
    actions.PlayEventAction.__init__(self, game, player, card=card)

  def resolve(self, response=None, ignore_clicks=False, ignore_all_costs=False):
    actions.PlayEventAction.resolve(
        self,
        response=response,
        ignore_clicks=ignore_clicks,
        ignore_all_costs=ignore_all_costs)
    modifiers.NumRndCardsToAccess(
        self.game, 2,
        server=self.game.corp.rnd,
        until=events.RunEnds)
    new_run = self.game.new_run(self.game.corp.rnd)
    new_run.begin()


class Card01036(event.Event):

  NAME = u"Card01036"
  SET = card_info.CORE
  NUMBER = 36
  SIDE = card_info.RUNNER
  FACTION = card_info.SHAPER
  INFLUENCE = 2
  UNIQUE = False
  KEYWORDS = set([
      card_info.RUN,
  ])
  COST = 2
  IMAGE_SRC = '01036.png'

  def build_actions(self):
    event.Event.build_actions(self)
    self._play_event_action = Card01036RunAction(
        self.game, self.player, card=self)
