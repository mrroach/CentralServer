from csrv.model.actions import action


class Subroutine(action.Action):
  def __init__(self, game, player, card=None):
    action.Action.__init__(self, game, player, card=card)
    self.is_broken = False
    self._is_mandatory = True
