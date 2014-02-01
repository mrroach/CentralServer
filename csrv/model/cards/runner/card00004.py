from csrv.model import actions
from csrv.model.actions import play_run_event
from csrv.model import events
from csrv.model import pool
from csrv.model import timing_phases
from csrv.model.cards import card_info
from csrv.model.cards import event


class Card00004(event.Event):

  NAME = u'Card00004'
  SET = card_info.CORE
  NUMBER = 4
  SIDE = card_info.RUNNER
  FACTION = card_info.ANARCH
  INFLUENCE = 1
  UNIQUE = False
  KEYWORDS = set([
      card_info.RUN,
  ])
  COST = 0
  IMAGE_SRC = '01004.png'

  def __init__(self, game, player):
    event.Event.__init__(self, game, player)
    self.pool = None

  def build_actions(self):
    event.Event.build_actions(self)
    self._play_event_action = play_run_event.PlayRunEvent(
        self.game, self.player, self)

  def play(self):
    self.pool = pool.EphemeralCreditPool(self.game, self.player, 9)
    self.game.runner.credit_pools.add(self.pool)
    self.game.register_listener(events.RunEnds, self)

  def on_run_ends(self, sender, event):
    self.player.credit_pools.remove(self.pool)
    self.game.deregister_listener(events.RunEnds, self)
    self.game.insert_next_phase(
        timing_phases.TakeBrainDamage(self.game, self.player, 1))
    self.game.current_phase().begin()
