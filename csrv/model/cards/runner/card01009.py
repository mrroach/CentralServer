from csrv.model import actions
from csrv.model import cost
from csrv.model import errors
from csrv.model import parameters
from csrv.model import timing_phases
from csrv.model.cards import card_info
from csrv.model.cards import program


class Card01009RetrieveVirusAction(actions.Action):
  REQUEST_CLASS = parameters.StackCardRequest
  DESCRIPTION = ('[click], 1[credit]: Search your stack for a virus program, '
                 'reveal it, and add it to your grip. Shuffle your stack.')

  def __init__(self, game, player, card):
    cost_obj = cost.SimpleCost(game, player, credits=1, clicks=1)
    actions.Action.__init__(self, game, player, card, cost=cost_obj)

  def resolve(self, response=None, ignore_clicks=False, ignore_all_costs=False):
    if not response or not response.card:
      raise errors.InvalidResponse('You must select a card')
    if not response.card.location == self.player.stack:
      raise errors.InvalidResponse('You must select a card from the stack')
    actions.Action.resolve(
        self, response, ignore_clicks=ignore_clicks,
        ignore_all_costs=ignore_all_costs)
    self.player.grip.add(response.card)
    self.player.stack.shuffle()


class Card01009(program.Program):

  NAME = u'Card01009'
  SET = card_info.CORE
  NUMBER = 9
  SIDE = card_info.RUNNER
  FACTION = card_info.ANARCH
  INFLUENCE = 2
  UNIQUE = False
  KEYWORDS = set([
      card_info.DAEMON,
  ])
  COST = 2
  MEMORY = 1
  HOST_MEMORY = 3

  IMAGE_SRC = '01009.png'

  WHEN_INSTALLED_PROVIDES_CHOICES_FOR = {
      timing_phases.RunnerTurnActions: 'retrieve_virus_actions',
  }

  def build_actions(self):
    program.Program.build_actions(self)
    self._retrieve_virus_action = Card01009RetrieveVirusAction(
        self.game, self.player, self)

  def retrieve_virus_actions(self):
    return [self._retrieve_virus_action]

  def can_host(self, card):
    if (isinstance(card, program.Program) and
        not card_info.ICEBREAKER in card.KEYWORDS):
      return True
    return False

  def free_memory(self):
    used = sum([c.memory for c in self.hosted_cards])
    return self.HOST_MEMORY - used

  def meets_memory_limits(self, card=None):
    free_mem = self.free_memory()
    if free_mem < 0:
      return False
    if card and card.memory > free_mem:
      return False
    return True

  def hosted_card_memory(self, card):
    """This assumes that the card passed in actually is hosted."""
    return 0

  def on_install(self):
    program.Program.on_install(self)
    self.game.register_response_target(
        parameters.InstallProgramRequest, 'host', self)

  def on_uninstall(self):
    program.Program.on_uninstall(self)
    self.game.deregister_response_target(
        parameters.InstallProgramRequest, 'host', self)
