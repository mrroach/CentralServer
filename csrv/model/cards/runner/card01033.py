from csrv.model import events
from csrv.model import modifiers
from csrv.model.cards import card_info
from csrv.model.cards import identity


class Card01033(identity.Identity):

  NAME = u'Card01033'
  SET = card_info.CORE
  NUMBER = 33
  SIDE = card_info.RUNNER
  FACTION = card_info.SHAPER
  UNIQUE = False
  KEYWORDS = set([
      card_info.NATURAL,
  ])
  BASE_LINK = 1
  IMAGE_SRC = '01033.png'

  LISTENS = [
      events.CorpTurnBegin,
      events.RunnerTurnBegin,
      events.CorpTurnEnd,
      events.RunnerTurnEnd,
      events.InstallProgram,
      events.InstallHardware,
  ]

  def __init__(self, game, player):
    identity.Identity.__init__(self, game, player)
    self.modifiers = []

  def on_runner_turn_begin(self, sender, event):
    # TODO(mrroach): this applies to installed cards too, which is not good
    self.modifiers = [
        modifiers.ProgramCostModifier(self.game, -1),
        modifiers.HardwareCostModifier(self.game, -1)]

  on_corp_turn_begin = on_runner_turn_begin

  def on_runner_turn_end(self, sender, event):
    for mod in self.modifiers:
      mod.remove()
    self.modifiers = []

  on_corp_turn_end = on_runner_turn_end
  on_install_program = on_runner_turn_end
  on_install_hardware = on_runner_turn_end

  def build_actions(self):
    identity.Identity.build_actions(self)

