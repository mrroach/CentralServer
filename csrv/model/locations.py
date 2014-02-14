import random
from csrv.model import actions
from csrv.model import errors
from csrv.model import game_object
from csrv.model import modifiers
from csrv.model import timing_phases


class Location(game_object.PlayerObject):
  def __init__(self, game, player, parent=None):
    game_object.PlayerObject.__init__(self, game, player)
    self.parent = parent
    self.cards = []
    self.set_new_id()

  @property
  def size(self):
    return len(self.cards)

  def add(self, card):
    if card.location:
      card.location.remove(card)
    card.location = self
    self.cards.append(card)

  def remove(self, card):
    self.cards.remove(card)
    card.location = None

  def shuffle(self):
    random.shuffle(self.cards)

  def pop(self):
    try:
      card = self.cards.pop()
    except IndexError:
      raise errors.DrawFromEmptyServer()
    card.location = None
    return card

  def push(self, card):
    return self.add(card)

  def pick(self):
    return random.choice(self.cards)


class Grip(Location):

  PROVIDES_CHOICES_FOR = {
      timing_phases.RunnerTurnDiscard: 'discard_actions',
  }

  def discard_actions(self):
    if self.size > self.player.max_hand_size:
      return [actions.Discard(self.game, self.player, c) for c in self.cards]
    return []

  def add(self, card):
    Location.add(self, card)
    card.on_enter_hand()

  def remove(self, card):
    Location.remove(self, card)
    card.on_exit_hand()


class Heap(Location):

  def add(self, card):
    Location.add(self, card)
    card.on_enter_heap()

  def remove(self, card):
    Location.remove(self, card)
    card.on_exit_heap()


class Stack(Location):

  def add(self, card):
    Location.add(self, card)
    card.on_enter_stack()

  def remove(self, card):
    Location.remove(self, card)
    card.on_exit_stack()


class Rig(Location):

  def add(self, card):
    Location.add(self, card)
    card.on_install()

  def remove(self, card):
    Location.remove(self, card)
    card.on_uninstall()


class Server(game_object.PlayerObject):
  """Base class for servers."""

  PROVIDES_CHOICES_FOR = {
      timing_phases.RunnerTurnActions: 'make_a_run_actions',
      timing_phases.RunEvent: 'make_a_run_actions',
  }
  NAME = 'server'

  def __init__(self, game, player):
    game_object.PlayerObject.__init__(self, game, player)
    self.installed = Location(self.game, self.player, self)
    self.ice = Location(self.game, self.player, self)
    self._current_access_list = None
    self.set_new_id()

  def __str__(self):
    return self.NAME

  def restricted_access(self):
    """Return cards which restrict what cards we can access."""
    restrictions = self.game.modifiers[
        modifiers.CardAccessRestriction].server_scope[self]
    return [r.access_card for r in restrictions]

  def cards_to_access(self, additional=None):
    restriction = self.restricted_access()
    if restriction:
      return restriction
    cards = list(self.installed.cards)
    if additional:
      cards += additional
    return cards

  def on_access(self):
    self._current_access_list = self.cards_to_access()
    self.game.register_choice_provider(
        timing_phases.ApproachServer_4_5, self, 'access_cards_actions')

  def on_access_end(self):
    self.game.run.accessed_cards.clear()
    self.game.deregister_choice_provider(
        timing_phases.ApproachServer_4_5, self, 'access_cards_actions')

  def access_cards_actions(self):
    return [actions.AccessCard(self.game, self.game.runner, card, self)
        for card in self._current_access_list]

  def on_access_card(self, card):
    self._current_access_list.remove(card)
    self.game.run.accessed_cards.add(card)
    self.game.insert_next_phase(
        timing_phases.AccessCard(self.game, self.game.runner, card))

  def access_cards(self):
    for card in self.cards_to_access():
      # begin advertising access actions
      card.on_access()

  def remove(self, card):
    if card.location == self.installed:
      self.uninstall(card)
    if card.location == self.ice:
      self.uninstall_ice(card)

  def install(self, card):
    """Install a card in a server."""
    self.installed.add(card)
    card.is_installed = True
    card.on_install()

  def uninstall(self, card):
    """Remove a card from a server."""
    self.installed.remove(card)
    card.is_installed = False
    card.derez()
    card.on_uninstall()

  def install_ice(self, card):
    self.ice.add(card)
    card.is_installed = True
    card.on_install()

  def uninstall_ice(self, card):
    self.ice.remove(card)
    card.is_installed = False
    card.on_uninstall()

  def make_a_run_actions(self):
    if self.game.runner.clicks.value:
      return [actions.MakeARunAction(self.game, self.game.runner, self)]
    return []


class CentralServer(Server, Location):

  def __init__(self, game, player):
    Server.__init__(self, game, player)
    Location.__init__(self, game, player)

  def remove(self, card):
    if card.location == self.installed:
      self.uninstall(card)
    elif card.location == self.ice:
      self.uninstall_ice(card)
    else:
      Location.remove(self, card)


class RemoteServer(Server):
  """A remote server."""

  NAME = 'Remote server'

  def __init__(self, game, player, idx=None):
    Server.__init__(self, game, player)
    self.idx = idx

  def __str__(self):
    return '%s %d' % (self.NAME, self.idx)

  def uninstall(self, card):
    """Remove a card from a server."""
    Server.uninstall(self, card)
    if not self.ice.cards and not self.installed.cards:
      self.game.corp.remove_remote_server(self)

  def uninstall_ice(self, card):
    """Remove ice from a server."""
    Server.uninstall_ice(self, card)
    if not self.ice.cards and not self.installed.cards:
      self.game.corp.remove_remote_server(self)



class Archives(CentralServer):
  NAME = 'Archives'

  def add(self, card):
    CentralServer.add(self, card)
    card.on_enter_archives()

  def remove(self, card):
    CentralServer.remove(self, card)
    card.on_exit_archives()

  def on_access(self):
    for card in self.cards:
      card.is_faceup = True
    CentralServer.on_access(self)

  def cards_to_access(self):
    return CentralServer.cards_to_access(self, self.cards)


class HQ(CentralServer):
  NAME = 'HQ'

  PROVIDES_CHOICES_FOR = {
      timing_phases.RunnerTurnActions: 'make_a_run_actions',
      timing_phases.RunEvent: 'make_a_run_actions',
      timing_phases.CorpTurnDiscard: 'discard_actions',
  }

  def discard_actions(self):
    if self.size > self.player.max_hand_size:
      return [actions.Discard(self.game, self.player, c) for c in self.cards]
    return []

  def num_cards_to_access(self):
    num = 1
    for modifier in self.game.modifiers[
        modifiers.NumHqCardsToAccess].server_scope[self]:
      num += modifier.value
    return num

  def cards_to_access(self, additional=None):
    num = self.num_cards_to_access()
    hand_cards = random.sample(self.cards, num)
    return CentralServer.cards_to_access(self, additional=hand_cards)

  def add(self, card):
    CentralServer.add(self, card)
    card.on_enter_hand()

  def remove(self, card):
    CentralServer.remove(self, card)
    card.on_exit_hand()


class RnD(CentralServer):
  NAME = 'R&D'

  def num_cards_to_access(self):
    num = 1
    for modifier in self.game.modifiers[
        modifiers.NumRndCardsToAccess].server_scope[self]:
      num += modifier.value
    return num

  def rnd_cards_to_access(self):
    num = self.num_cards_to_access()
    return list(reversed(self.cards[-num:]))

  def on_access(self):
    self._current_access_list = self.cards_to_access()
    self._current_rnd_access_list = self.rnd_cards_to_access()
    self.game.register_choice_provider(
        timing_phases.ApproachServer_4_5, self, 'access_cards_actions')

  def on_access_end(self):
    self.game.run.accessed_cards.clear()
    self.game.deregister_choice_provider(
        timing_phases.ApproachServer_4_5, self, 'access_cards_actions')

  def access_cards_actions(self):
    # allow accessing only the next card from rnd and upgrades
    cards = self._current_access_list + self._current_rnd_access_list[:1]
    return [actions.AccessCard(self.game, self.game.runner, card, self)
            for card in cards]

  def on_access_card(self, card):
    if card in self._current_access_list:
      self._current_access_list.remove(card)
    elif [card] == self._current_rnd_access_list[:1]:
      # the next call to access_cards_actions will get the next card
      self._current_rnd_access_list.remove(card)
    self.game.run.accessed_cards.add(card)
    self.game.insert_next_phase(
        timing_phases.AccessCard(self.game, self.game.runner, card))

  def add(self, card):
    CentralServer.add(self, card)
    card.on_enter_rnd()

  def remove(self, card):
    CentralServer.remove(self, card)
    card.on_exit_rnd()


class CorpScoreArea(Location):
  def add(self, card):
    Location.add(self, card)
    card.on_enter_corp_score_area()

  def remove(self, card):
    Location.remove(self, card)
    card.on_exit_corp_score_area()


class RunnerScoreArea(Location):
  def add(self, card):
    Location.add(self, card)
    card.on_enter_runner_score_area()

  def remove(self, card):
    Location.remove(self, card)
    card.on_exit_runner_score_area()


class Banished(Location):
  def add(self, card):
    Location.add(self, card)
    card.on_banish()
