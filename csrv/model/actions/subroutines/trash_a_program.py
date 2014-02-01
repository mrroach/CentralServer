import subroutine
from csrv.model.actions import trash
from csrv.model import timing_phases
from csrv.model.cards import program


class SelectProgramToTrashPhase(timing_phases.BasePhase):
  """Select and trash a program."""
  NULL_OK = False

  def choices(self, refresh=False):
    if self._choices is None or refresh:
      programs = [card for card in self.game.runner.rig.cards
                  if isinstance(card, program.Program)]
      self._choices = [
          trash.Trash(self.game, self.player, card) for card in programs]
    return self._choices

  def resolve(self, choice, response):
    timing_phases.BasePhase.resolve(self, choice, response)
    if choice or not self.choices(refresh=True):
      self.end_phase()


class TrashAProgram(subroutine.Subroutine):

  DESCRIPTION = 'Trash 1 program'

  def resolve(self, response=None):
    self.game.insert_next_phase(
        SelectProgramToTrashPhase(self.game, self.game.corp))
