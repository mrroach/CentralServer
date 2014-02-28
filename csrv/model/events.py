"""Events are notifications of game state changes.

Cards and identities can register their interest in, and respond to
specific types of events. These should be as general as possible in
order to minimize the number of event types that a listener needs
to subscribe to.
"""

import re
import sys
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


EVENTS = {
    'BeginCorpGameSetup': 'The corp draws a starting hand.',
    'CorpGameSetup': 'The corp may mulligan.',
    'BeginRunnerGameSetup': 'The runner draws a starting hand.',
    'RunnerGameSetup': 'The runner may mulligan.',
    'CorpTurnBegin': 'The beginning of the Corp\'s turn.',
    'CorpTurnEnd': 'The Corp\'s turn ends.',
    'RunnerTurnEnd': 'The Runner\'s turn ends.',
    'CorpTurnDraw': 'The corp must draw a card.',
    'CorpActionPhase': 'The corp takes actions.',
    'CorpDiscardPhase': 'The corp must discard down to max hand size.',
    'GainACredit': 'A click for a credit.',
    'InstallAgendaAssetUpgrade': 'An agenda, asset, or upgrade was installed.',
    'InstallIce': 'Ice was installed.',
    'UninstallCard': 'Generic event for any card being uninstalled.',
    'UninstallIce': 'Ice was uninstalled.',
    'InstallProgram': 'A program was installed.',
    'InstallHardware': 'A program was installed.',
    'DrawFromRnD': 'The corp draws a card from R&D.',
    'DrawFromStack': 'The runner draws a card from the stack.',
    'PurgeVirusCounters': 'The corp purges virus counters.',
    'RezAssetUpgrade': 'The corp rezzes an asset or upgrade.',
    'RezIce': 'The corp rezzes a piece of ice.',
    'IceStrengthChanged': 'The strength of a piece of ice changed.',
    'BeginRunnerTurnBegin': 'The very beginning of the runner\'s turn.',
    'RunnerTurnBegin': 'The beginning of the Runner\'s turn.',
    'RunnerActionPhase': 'The runner takes actions.',
    'RunnerDiscardPhase': 'The runner must discard down to max hand size.',
    'BeginEncounterIce_3_1':
        'Phase 3.1 of an ancounter with a piece of ice begins.',
    'BeginEncounterIce_3_2':
        'Phase 3.2 of an ancounter with a piece of ice begins.',
    'EndEncounterIce_3_2':
        'Phase 3.2 of an encounter with a piece of ice ends.',
    'BeginApproachIce_2_1': 'The runner approaches a piece of ice.',
    'BeginApproachServer_4_1': 'The runner approaches a server.',
    'ApproachServer_4_4': 'A run is successful.',
    'BeginApproachServer_4_5': 'Beginning of the approach server 4.5 phase.',
    'EndApproachServer_4_5': 'An access phase completes.',
    'RunBegins': 'A run begins.',
    'RunEnds': 'A run ends (either successfully or failed).',
    'UnsuccessfulRun': 'A run ends unsuccessfully.',
    'SuccessfulRun': 'A run ends successfully.',
    'EndTakeBrainDamage': 'A brain damage phase ends.',
    'EndTakeNetDamage': 'A net damage phase ends.',
    'EndTraceCorpBoost': 'The corp finishes boosting a trace.',
    'EndTraceRunnerBoost': 'The runner finishes boosting a trace.',
    'ScoreAgenda': 'The corp scores an agenda.',
    'StealAgenda': 'The runner steals an agenda.',
    'PlayOperation': 'The corp plays an operation.',
}

# Create the classes based on the dictionary above and set them as module
# attributes.
_THIS_MODULE = sys.modules[__name__]
for class_name, doc in EVENTS.iteritems():
  class_obj = type(class_name, (BaseEvent,), {'__doc__': doc})
  setattr(_THIS_MODULE, class_name, class_obj)
