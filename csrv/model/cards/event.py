from csrv.model import actions
from csrv.model.cards import card_base
from csrv.model import timing_phases
from csrv.model.cards import card_info


class Event(card_base.CardBase):
  """An event card which can be paid for and played into the heap."""

  TYPE = card_info.EVENT

  WHEN_IN_HAND_PROVIDES_CHOICES_FOR = {
      timing_phases.RunnerTurnActions: 'play_event_actions',
  }

  def build_actions(self):
    card_base.CardBase.build_actions(self)
    self._play_event_action = actions.PlayEventAction(
        self.game, self.player, self)

  def play_event_actions(self):
    if self.is_playable():
      return [self._play_event_action]
    else:
      return []

  def is_playable(self):
    return self._play_event_action.is_usable()

  def play(self):
    return
