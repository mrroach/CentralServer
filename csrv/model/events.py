"""Events are notifications of game state changes.

Cards and identities can register their interest in, and respond to
specific types of events. These should be as general as possible in
order to minimize the number of event types that a listener needs
to subscribe to.
"""

import re
from csrv.model import game_object

CALLBACK_RE = re.compile(r'\B((?<=[a-z])[A-Z]|[A-Z](?=[a-z]))')


class EventMeta(type):
  """A simple metaclass to add the callback name to event classes."""

  def __new__(mcs, name, bases, new_attrs):
    # ThingHappensEvent.callback => 'on_thing_happens_event'
    if 'callback' not in new_attrs or not new_attrs['callback']:
      new_attrs['callback'] = 'on_' + CALLBACK_RE.sub(r'_\1', name).lower()

    # ThingHappensEvent.description => ThingHappensEvent.__doc__
    if 'description' not in new_attrs or not new_attrs['description']:
      new_attrs['description'] = new_attrs['__doc__']

    return type.__new__(mcs, name, bases, new_attrs)


class BaseEvent(game_object.PlayerObject):
  """Base event type."""
  __metaclass__ = EventMeta


###
### Keep in alphabetical order, please.
###

class ApproachServer_4_4(BaseEvent):
  """A run is successful."""


class BeginApproachIce_2_1(BaseEvent):
  """The runner approaches a piece of ice."""


class BeginApproachServer_4_1(BaseEvent):
  """The runner approaches a server."""


class BeginApproachServer_4_5(BaseEvent):
  """Beginning of the approach server 4.5 phase."""


class BeginCorpGameSetup(BaseEvent):
  """The corp draws a starting hand."""


class BeginEncounterIce_3_1(BaseEvent):
  """Phase 3.1 of an ancounter with a piece of ice begins."""


class BeginEncounterIce_3_2(BaseEvent):
  """Phase 3.2 of an ancounter with a piece of ice begins."""


class BeginRunnerGameSetup(BaseEvent):
  """The runner draws a starting hand."""


class BeginRunnerTurnBegin(BaseEvent):
  """The very beginning of the runner's turn."""


class CorpActionPhase(BaseEvent):
  """The corp takes actions."""


class CorpDiscardPhase(BaseEvent):
  """The corp must discard down to max hand size."""


class CorpGameSetup(BaseEvent):
  """The corp may mulligan."""


class CorpTurnBegin(BaseEvent):
  """The beginning of the Corp's turn."""


class CorpTurnDraw(BaseEvent):
  """The corp must draw a card."""


class CorpTurnEnd(BaseEvent):
  """The Corp's turn ends."""


class DrawFromRnD(BaseEvent):
  """The corp draws a card from R&D."""


class DrawFromStack(BaseEvent):
  """The runner draws a card from the stack."""


class EndApproachServer_4_5(BaseEvent):
  """An access phase completes."""


class EndEncounterIce_3_2(BaseEvent):
  """Phase 3.2 of an encounter with a piece of ice ends."""


class EndTakeBrainDamage(BaseEvent):
  """A brain damage phase ends."""


class EndTakeNetDamage(BaseEvent):
  """A net damage phase ends."""


class EndTraceCorpBoost(BaseEvent):
  """The corp finishes boosting a trace."""


class EndTraceRunnerBoost(BaseEvent):
  """The runner finishes boosting a trace."""


class GainACredit(BaseEvent):
  """A click for a credit."""


class IceStrengthChanged(BaseEvent):
  """The strength of a piece of ice changed."""


class InstallAgendaAssetUpgrade(BaseEvent):
  """An agenda, asset, or upgrade was installed."""


class InstallHardware(BaseEvent):
  """A program was installed."""


class InstallIce(BaseEvent):
  """Ice was installed."""


class InstallProgram(BaseEvent):
  """A program was installed."""


class PlayOperation(BaseEvent):
  """The corp plays an operation."""


class PurgeVirusCounters(BaseEvent):
  """The corp purges virus counters."""

class RezAssetUpgrade(BaseEvent):
  """The corp rezzes an asset or upgrade."""


class RezIce(BaseEvent):
  """The corp rezzes a piece of ice."""


class RunBegins(BaseEvent):
  """A run begins."""


class RunEnds(BaseEvent):
  """A run ends (either successfully or failed)."""


class RunnerActionPhase(BaseEvent):
  """The runner takes actions."""


class RunnerDiscardPhase(BaseEvent):
  """The runner must discard down to max hand size."""


class RunnerGameSetup(BaseEvent):
  """The runner may mulligan."""


class RunnerTurnBegin(BaseEvent):
  """The beginning of the Runner's turn."""


class RunnerTurnEnd(BaseEvent):
  """The Runner's turn ends."""


class ScoreAgenda(BaseEvent):
  """The corp scores an agenda."""


class StealAgenda(BaseEvent):
  """The runner steals an agenda."""


class SuccessfulRun(BaseEvent):
  """A run ends successfully."""


class UninstallCard(BaseEvent):
  """Generic event for any card being uninstalled."""


class UninstallIce(BaseEvent):
  """Ice was uninstalled."""


class UnsuccessfulRun(BaseEvent):
  """A run ends unsuccessfully."""
