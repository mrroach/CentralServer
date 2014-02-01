"""Discard a card from hand."""

from csrv.model.actions import action


class Discard(action.Action):

  DESCRIPTION = 'Discard a card.'

  def resolve(self, response=None, ignore_clicks=False, ignore_all_costs=False):
    action.Action.resolve(
        self,
        ignore_clicks=ignore_clicks,
        ignore_all_costs=ignore_all_costs)
    self.game.log('The %s discards a card' % self.player, None)
    self.card.trash()

  @property
  def description(self):
    return 'Discard %s' % self.card.NAME
