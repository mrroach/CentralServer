from csrv.model import actions
from csrv.model import cost
from csrv.model import events
from csrv.model import timing_phases
from csrv.model.cards import card_info
from csrv.model.cards import program


class Card01051(program.Program):

  NAME = u'Card01051'
  SET = card_info.CORE
  NUMBER = 51
  SIDE = card_info.RUNNER
  FACTION = card_info.NEUTRAL
  INFLUENCE = 0
  UNIQUE = False
  KEYWORDS = set([
      card_info.AI,
      card_info.ICEBREAKER,
      card_info.VIRUS,
  ])
  COST = 5
  IMAGE_SRC = '01051.png'
  STRENGTH = 0
  MEMORY = 1

  WHEN_INSTALLED_PROVIDES_CHOICES_FOR = {
      timing_phases.RunnerTurnActions: 'place_virus_counter_actions',
      timing_phases.EncounterIce_3_1: 'interact_with_ice_actions',
  }

  def build_actions(self):
    program.Program.build_actions(self)
    self._place_virus_counter = actions.CardClickAbility(
        self.game, self.player, self,
        '[click]: Place 1 virus counter on Card01051',
        'place_virus_counter',
        cost=cost.SimpleCost(self.game, self.player, clicks=1),)
    self._boost_strength_action = actions.BoostBreakerStrength(
        self.game, self.player, self, strength=1, credits=1)

  def interact_with_ice_actions(self):
    return ([self._boost_strength_action] +
        [actions.AiBreakSubroutine(
            self.game, self.player, self, sub)
         for sub in self.game.run.current_ice().subroutines])

  def place_virus_counter_actions(self):
    return [self._place_virus_counter]

  def place_virus_counter(self):
    self.virus_counters += 1

  def on_used_to_break_subroutine(self):
    self.game.register_listener(events.EndEncounterIce_3_2, self)

  def on_end_encounter_ice_3_2(self, sender, event):
    if self.virus_counters:
      self.virus_counters -= 1
    else:
      self.game.insert_next_phase(
          timing_phases.TrashAProgram(self.game, self.player, self))
