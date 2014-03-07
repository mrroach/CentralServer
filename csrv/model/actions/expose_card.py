from csrv.model.actions import action
from csrv.model import errors
from csrv.model import parameters


class ExposeCard(action.Action):
  REQUEST_CLASS = parameters.TargetInstalledCorpCardRequest
  DESCRIPTION = 'Expose an installed card belonging to the corp'

  def resolve(self, response=None, ignore_clicks=False, ignore_all_costs=False):
    if (response and response.card and
        response.card.player == self.game.corp and
        response.card.is_installed):
      action.Action.resolve(
          self, response,
          ignore_clicks=ignore_clicks,
          ignore_all_costs=ignore_all_costs)
      # TODO(mrroach): This needs to be an interruptable phase
      self.game.log('The runner exposes %s' % response.card)
      self.game.expose_card(response.card)
    else:
      raise errors.InvalidResponse(
          'You must select an installed card belonging to the corp')
