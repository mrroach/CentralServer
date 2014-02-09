from csrv.model import actions
from csrv.model import events
from csrv.model.cards import card_base
from csrv.model import timing_phases
from csrv.model.cards import card_info


class Operation(card_base.CardBase):
  """An operation card which can be paid for and played into archives."""

  TYPE = card_info.OPERATION

  WHEN_IN_HAND_PROVIDES_CHOICES_FOR = {
      timing_phases.CorpTurnActions: 'play_operation_actions',
  }

  def build_actions(self):
    card_base.CardBase.build_actions(self)
    self._play_operation_action = actions.PlayOperationAction(
        self.game, self.player, self)

  def play_operation_actions(self):
    if self.is_playable():
      return [self._play_operation_action]
    else:
      return []

  def is_playable(self):
    return (self.player.clicks.value and
            self.COST <= self.player.credits.value)

  def play(self):
    self.trigger_event(events.PlayOperation(self.game, self.player))
