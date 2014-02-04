from csrv.model import actions
from csrv.model.actions import play_run_event
from csrv.model import cost
from csrv.model import events
from csrv.model import timing_phases
from csrv.model.cards import card_info
from csrv.model.cards import event


class TrashForFree(actions.TrashOnAccess):
  COST_CLASS = cost.NullCost

  def is_usable(self):
    return actions.TrashOnAccess.is_usable(self) and self.card.is_being_accessed


class Card01003Action(play_run_event.PlayRunEvent):

  def resolve(self, response=None, ignore_clicks=False, ignore_all_costs=False):
    play_run_event.PlayRunEvent.resolve(
        self, response, ignore_clicks=ignore_clicks,
        ignore_all_costs=ignore_all_costs)
    self.game.register_choice_provider(
        timing_phases.AccessCard, self, 'access_card_actions')
    self.game.register_listener(events.RunEnds, self)

  def access_card_actions(self):
    card = self.game.current_phase().card  # blech
    return [TrashForFree(self.game, self.player, card)]

  def on_run_ends(self, sender, event):
    self.game.deregister_choice_provider(
        timing_phases.AccessCard, self, 'access_card_actions')
    self.game.deregister_listener(events.RunEnds, self)


class Card01003(event.Event):

  NAME = u'Card01003'
  SET = card_info.CORE
  NUMBER = 3
  SIDE = card_info.RUNNER
  FACTION = card_info.ANARCH
  INFLUENCE = 2
  UNIQUE = False
  KEYWORDS = set([
      card_info.RUN,
      card_info.SABOTAGE,
  ])
  COST = 2
  IMAGE_SRC = '01003.png'

  def build_actions(self):
    event.Event.build_actions(self)
    self._play_event_action = Card01003Action(self.game, self.player, self)
