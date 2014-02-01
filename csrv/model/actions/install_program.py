"""Base actions for the players to take."""

from csrv.model.actions import action
from csrv.model import appropriations
from csrv.model import cost
from csrv.model import errors
from csrv.model import events
from csrv.model import game_object
from csrv.model import parameters
from csrv.model.cards import card_info


class InstallProgram(action.Action):

  DESCRIPTION = '[click]: Install a program'
  COST_CLASS = cost.InstallProgramCost
  REQUEST_CLASS = parameters.InstallProgramRequest

  def __init__(self, game, player, card=None, cost=None):
    action.Action.__init__(self, game, player, card=card, cost=cost)
    self.cost.appropriations.append(appropriations.INSTALL_PROGRAMS)
    if card_info.VIRUS in card.KEYWORDS:
      self.cost.appropriations.append(appropriations.INSTALL_VIRUSES)

  def resolve(self, response=None, ignore_clicks=False, ignore_all_costs=False):
    if (not ignore_all_costs and
        not self.cost.can_pay(response, ignore_clicks)):
      raise errors.CostNotSatisfied(
          'Not enough credits to install in that location.')
    if response and response.programs_to_trash:
      for program in response.programs_to_trash:
        if program.location != self.game.runner.rig:
          raise errors.InvalidResponse("You can't trash that")
        program.trash()

    if response and response.host:
      if not response.host in self.card.install_host_targets():
        raise errors.InvalidResponse(
            'Cannot host this type of card')
      if not response.host.meets_memory_limits(self.card):
        raise errors.InvalidResponse(
            'Host does not have enough memory free')
      response.host.host_card(self.card)
    action.Action.resolve(self, response,
        ignore_clicks=ignore_clicks,
        ignore_all_costs=ignore_all_costs)
    self.player.rig.add(self.card)

  @property
  def description(self):
    return 'Install %s' % self.card.NAME


