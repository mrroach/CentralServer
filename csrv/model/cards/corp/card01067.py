from csrv.model import events
from csrv.model import timing_phases
from csrv.model.cards import card_info
from csrv.model.cards import identity


class Card01067(identity.Identity):

  NAME = u'Card01067'
  SET = card_info.CORE
  NUMBER = 67
  SIDE = card_info.CORP
  FACTION = card_info.NETCORP
  UNIQUE = False
  KEYWORDS = set([
      card_info.MEGACORP,
  ])
  IMAGE_SRC = '01067.png'

  LISTENS = [
      events.ScoreAgenda,
      events.StealAgenda,
  ]
  def build_actions(self):
    identity.Identity.build_actions(self)

  def on_score_agenda(self, sender, event):
    self._do_damage()

  def on_steal_agenda(self, sender, event):
    self._do_damage()

  def _do_damage(self):
    self.log('The runner takes damage from the corp\'s ability')
    self.game.insert_next_phase(
        timing_phases.TakeNetDamage(self.game, self.game.runner, 1))
