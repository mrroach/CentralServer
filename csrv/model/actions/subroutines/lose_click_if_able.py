import subroutine


class LoseClickIfAble(subroutine.Subroutine):

  DESCRIPTION = 'The Runner loses [click], if able.'

  def resolve(self, response=None):
    if self.game.runner.clicks.value:
      self.game.runner.clicks.lose(1)
