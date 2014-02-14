from csrv.model import actions
from csrv.model import timing_phases
from csrv.model.cards import card_info
from csrv.model.cards import hardware


class FetchAndInstallOther(actions.InstallHardware):
  DESCRIPTION = ('Fetch and install another copy of Card01039.'
                 ' Shuffle your stack.')

  def resolve(self, response=None, ignore_clicks=False, ignore_all_costs=False):
    actions.Action.resolve(self, response,
                           ignore_clicks=ignore_clicks,
                           ignore_all_costs=ignore_all_costs)
    self.player.stack.shuffle()


class DoNotFetch(actions.Action):
  DESCRIPTION = 'Do not fetch another copy of Card01039'


class DecideInstallOther(timing_phases.ActivateAbilityChoice):
  """Decide whether to install another copy of Card01039."""


class Card01039(hardware.Hardware):

  NAME = u'Card01039'
  SET = card_info.CORE
  NUMBER = 39
  SIDE = card_info.RUNNER
  FACTION = card_info.SHAPER
  INFLUENCE = 1
  UNIQUE = False
  KEYWORDS = set([
      card_info.LINK,
  ])
  COST = 2
  IMAGE_SRC = '01039.png'

  def build_actions(self):
    hardware.Hardware.build_actions(self)

  def on_install(self):
    hardware.Hardware.on_install(self)
    self.player.link.gain(1)
    others = [c for c in self.player.stack.cards
              if c.NAME == self.NAME]
    if others:
      yes_action = FetchAndInstallOther(self.game, self.player, others[0])
      no_action = DoNotFetch(self.game, self.player)
      self.game.insert_next_phase(
          DecideInstallOther(self.game, self.player,
                             yes_action, no_action, None))

  def on_uninstall(self):
    hardware.Hardware.on_uninstall(self)
    self.player.link.lose(1)

