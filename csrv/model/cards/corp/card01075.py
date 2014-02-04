from csrv.model import events
from csrv.model import modifiers
from csrv.model import timing_phases
from csrv.model.actions.subroutines import subroutine
from csrv.model.cards import card_info
from csrv.model.cards import ice


class Card01075Subroutine(subroutine.Subroutine):
  DESCRIPTION = ('The next piece of ice the runner encounters during this run '
                 'has +2 strength. Do 3 net damage unless the Runner breaks '
                 'all subroutines on that piece of ice.')

  def resolve(self, response=None):
    self.card.log('Card01075 is watching...')
    self.card.watch_for_next_encounter()


class Card01075(ice.Ice):

  NAME = u'Card01075'
  SET = card_info.CORE
  NUMBER = 75
  SIDE = card_info.CORP
  FACTION = card_info.NETCORP
  INFLUENCE = 1
  UNIQUE = False
  KEYWORDS = set([
      card_info.CODE_GATE,
  ])
  COST = 1
  IMAGE_SRC = '01075.png'
  STRENGTH = 4

  def __init__(self, game, player):
    ice.Ice.__init__(self, game, player)
    self.subroutines = [
        Card01075Subroutine(game, player, card=self),
    ]
    self._watched_ice = None

  def build_actions(self):
    ice.Ice.build_actions(self)

  def watch_for_next_encounter(self):
    self.game.register_listener(events.BeginEncounterIce_3_1, self)
    self.game.register_listener(events.RunEnds, self)

  def on_begin_encounter_ice_3_1(self, sender, event):
    self.game.deregister_listener(events.BeginEncounterIce_3_1, self)
    self.game.register_listener(events.BeginApproachIce_2_1, self)
    self.game.register_listener(events.BeginApproachServer_4_1, self)
    self._watched_ice = self.game.run.current_ice()
    modifiers.IceStrengthModifier(
        self.game, 2,
        card=self._watched_ice,
        until=events.EndEncounterIce_3_2)

  def on_run_ends(self, sender, event):
    if self._watched_ice:
      self.check_for_net_damage()
    else:
      # The run ended without more ice being encountered
      self.game.deregister_listener(events.BeginEncounterIce_3_1, self)
      self.game.deregister_listener(events.RunEnds, self)

  def on_begin_approach_ice_2_1(self, sender, event):
    self.check_for_net_damage()

  def on_begin_approach_server_4_1(self, sender, event):
    self.check_for_net_damage()

  def check_for_net_damage(self):
    self.game.deregister_listener(events.BeginApproachIce_2_1, self)
    self.game.deregister_listener(events.BeginApproachServer_4_1, self)
    self.game.deregister_listener(events.RunEnds, self)
    watched_ice = self._watched_ice
    self._watched_ice = None
    for subroutine in watched_ice.subroutines:
      if not subroutine.is_broken:
        self.do_net_damage()
        break

  def do_net_damage(self):
    self.log('Card01075 found unbroken subroutines')
    self.game.insert_next_phase(
        timing_phases.TakeNetDamage(self.game, self.game.runner, 3))
