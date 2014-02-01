import subroutine
from csrv.model import events
from csrv.model import timing_phases


class DoNetDamage(subroutine.Subroutine):

  DESCRIPTION = 'Do 1 net damage.'

  def __init__(self, game, player, card=None, damage=1):
    subroutine.Subroutine.__init__(self, game, player, card=card)
    self.damage = damage

  def resolve(self, response=None):
    self.game.insert_next_phase(
        timing_phases.TakeNetDamage(self.game, self.game.runner, self.damage))

  @property
  def description(self):
    return 'Do %s net damage.' % self.damage
