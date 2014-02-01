import subroutine
from csrv.model.actions import take_brain_damage
from csrv.model import events
from csrv.model import timing_phases


class DoBrainDamage(subroutine.Subroutine):

  DESCRIPTION = 'Do 1 brain damage.'

  def resolve(self, response=None):
    self.game.insert_next_phase(
        timing_phases.TakeBrainDamage(self.game, self.game.runner, 1))

