import subroutine


class EndTheRun(subroutine.Subroutine):

  DESCRIPTION = 'End the run'

  def resolve(self, response=None):
    self.game.run.end()

