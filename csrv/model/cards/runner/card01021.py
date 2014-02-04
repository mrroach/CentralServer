from csrv.model import events
from csrv.model.actions import play_run_event
from csrv.model.cards import card_info
from csrv.model.cards import event


class Card01021(event.Event):

  NAME = u'Card01021'
  SET = card_info.CORE
  NUMBER = 21
  SIDE = card_info.RUNNER
  FACTION = card_info.CRIMINAL
  INFLUENCE = 3
  UNIQUE = False
  KEYWORDS = set([
      card_info.RUN,
  ])
  COST = 2
  IMAGE_SRC = '01021.png'

  def build_actions(self):
    event.Event.build_actions(self)
    self._play_event_action = play_run_event.PlayRunEvent(
        self.game, self.player, self)

  def play(self):
    self.game.register_listener(events.BeginEncounterIce_3_1, self)
    self.game.register_listener(events.RunEnds, self)

  def on_begin_encounter_ice_3_1(self, sender, event):
    self.game.deregister_listener(events.BeginEncounterIce_3_1, self)
    self.game.deregister_listener(events.RunEnds, self)
    self.game.run.bypass_ice = True
    self.game.current_phase().end_phase()

  def on_run_ends(self, sender, event):
    self.game.deregister_listener(events.BeginEncounterIce_3_1, self)
    self.game.deregister_listener(events.RunEnds, self)

