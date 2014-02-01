from csrv.model.actions import action


class AccessCard(action.Action):

  DESCRIPTION = 'Access a card in a server'

  def __init__(self, game, player, card, server):
    action.Action.__init__(self, game, player, card)
    self.server = server

  def resolve(self, response=None, ignore_clicks=False, ignore_all_costs=False):
    self.server.on_access_card(self.card)

  @property
  def description(self):
    if self.card.is_faceup:
      return 'Access %s' % self.card
    else:
      return 'Access unrezzed card'
