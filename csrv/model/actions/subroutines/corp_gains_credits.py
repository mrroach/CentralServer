import subroutine


class CorpGainsCredits(subroutine.Subroutine):

  DESCRIPTION = 'The corp gains credits.'

  def __init__(self, game, player, credits=1):
    subroutine.Subroutine.__init__(self, game, player)
    self.credits = credits

  def resolve(self, response=None):
    subroutine.Subroutine.resolve(self, response=response)
    self.game.corp.credits.gain(self.credits)

  @property
  def description(self):
    return 'The corp gains %s [credits]' % self.credits
