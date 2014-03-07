import json
import random
from csrv.model import parameters


def deserialize_response(game, data):
  response_class = getattr(parameters, data['response_type'])
  response = response_class()
  response.merge_from_dict(game, data['response_data'])
  return response


class JsonSerializer(object):
  """Serialize game state to Json"""

  def __init__(self, game):
    self.game = game

  def serialize_game_corp(self):
    """Serialize the game from the corp's point of view.

    Here "for the corp" means that the runner's hand and deck are not
    included (counts are given instead). And the identifiers for the cards
    in the corp's deck are given, but obviously not their position in the
    deck.
    """
    game = self.game
    if game.run and game.run.server == game.corp.rnd:
      run_hidden = True
    else:
      run_hidden = False

    top_level = {
        'choice_count': game.choice_count,
        'corp_turn_count': game.corp_turn_count,
        'runner_turn_count': game.runner_turn_count,
        'active_player': str(game.active_player),
        'corp': self.serialize_corp(),
        'runner': self.serialize_runner(game.runner),
        'run': self.serialize_run(hidden=run_hidden),
        'choices': self.render_choices(
            game.current_phase().player != game.corp),
    }

    return json.dumps(top_level)

  def serialize_game_runner(self):
    """Serialize the game from the runner's point of view.

    Mostly this means hiding corp cards and unhiding runner cards.
    """
    game = self.game
    top_level = {
        'choice_count': game.choice_count,
        'corp_turn_count': game.corp_turn_count,
        'runner_turn_count': game.runner_turn_count,
        'active_player': str(game.active_player),
        'corp': self.serialize_corp(hidden=True),
        'runner': self.serialize_runner(hidden=False),
        'run': self.serialize_run(),
        'choices': self.render_choices(
            game.current_phase().player != game.runner),
        }
    return json.dumps(top_level)

  def render_choices(self, secret=False):
    phase = self.game.current_phase()
    data = {
        'phase': phase.__class__.__name__,
        'description': phase.description,
        'player': str(phase.player),
    }
    if not secret:
      choices = phase.choices()
      data['choices'] = [self.render_choice(c) for c in choices]
      data['null_ok'] = phase.NULL_OK
      if phase.NULL_OK:
        data['null_choice'] = phase.null_choice
    return data

  def serialize_choices(self, secret=False):
    data = self.render_choices(secret)
    return json.dumps(data)

  def render_choice(self, choice):
    if choice.card:
      card = self.serialize_card(choice.card)
    else:
      card = None
    request = choice.request()
    if hasattr(choice, 'server') and choice.server:
      server = choice.server.game_id
    else:
      server = None
    data = {
        'description': choice.description,
        'type': choice.__class__.__name__,
        'request': request.__class__.__name__,
        'card': card,
        'server': server,
        'cost': str(choice.cost),
        'is_mandatory': choice.is_mandatory,
        'valid_response_options': request.valid_response_options(),
    }
    return data

  def serialize_corp(self, hidden=False):
    """Serialize the corp's info including money, counters, servers.

    Args:
      hidden: bool, Whether facedown cards should be hidden.
    """
    corp = self.game.corp

    return {
        'clicks': corp.clicks.value,
        'credits': corp.credits.value,
        'bad_publicity': corp.bad_publicity,
        'agenda_points': corp.agenda_points,
        'scored_agendas': [self.serialize_card(c)
                           for c in corp.scored_agendas.cards],
        'identity': self.serialize_minimal(corp.identity),
        'hq': self.serialize_central(corp.hq, hidden=hidden, card_count=hidden),
        'archives': self.serialize_central(
            corp.archives, shuffle=True, hidden=hidden),
        'rnd': self.serialize_central(
            corp.rnd, shuffle=True, hidden=hidden, card_count=hidden),
        'remotes': [self.serialize_remote(s, hidden=hidden)
                    for s in corp.remotes],
    }

  def serialize_runner(self, hidden=False):
    """Serialize the runner's info including money, counters, rig.

    Args:
      hidden: bool, Whether grip and stack should be hidden.
    """
    runner = self.game.runner
    # Sum all the general-purpose pools
    credits = sum([p.value for p in runner.find_pools()])

    return {
        'clicks': runner.clicks.value,
        'credits': credits,
        'agenda_points': runner.agenda_points,
        'brain_damage': runner.brain_damage,
        'link': runner.link.value,
        'tags': runner.tags,
        'scored_agendas': [self.serialize_card(c)
                           for c in runner.scored_agendas.cards],
        'identity': self.serialize_minimal(runner.identity),
        'grip': [self.serialize_minimal(c, hidden=hidden)
                 for c in runner.grip.cards],
        'heap': [self.serialize_minimal(c, hidden=hidden)
                 for c in runner.heap.cards],
        'stack': [self.serialize_minimal(c, hidden=hidden) for c in
                  sorted(runner.stack.cards, key=lambda x: (x.SET, x.NUMBER))],
        'rig': [self.serialize_card(c, hidden=hidden)
                for c in runner.rig.cards],
        'free_memory': runner.free_memory,
    }

  def serialize_run(self, hidden=False):
    run = self.game.run
    if not run:
      return None
    if run.current_ice():
      ice = self.serialize_minimal(run.current_ice(), hidden=True)
    else:
      ice = None

    data = {
        'server': run.server.game_id,
        'current_ice': ice,
    }
    if hidden:
      data['accessed_cards'] = [{} for c in run.accessed_cards]
    else:
      data['accessed_cards'] = [self.serialize_card(c, hidden=hidden)
                                for c in run.accessed_cards]
    return data

  def serialize_card(self, card, hidden=False):
    data = {
        'is_rezzed': card.is_rezzed,
        'is_faceup': card.is_faceup,
        'advancement_tokens': card.advancement_tokens,
        'agenda_counters': card.agenda_counters,
        'credits': card.credits,
        'virus_counters': card.virus_counters,
        'game_id': card.game_id,
        'host': card.host.game_id if card.host else None,
        'hosted_cards': [c.game_id for c in card.hosted_cards],
    }

    if card.is_faceup or card.is_exposed or not hidden:
      data['set'] = card.SET
      data['number'] = card.NUMBER
      data['name'] = card.NAME
    return data

  def serialize_minimal(self, card, hidden=False):
    """Return a minimal set of info on a card."""
    data = {
        'game_id': card.game_id,
        'host': card.host.game_id if card.host else None,
    }
    if card.is_faceup or card.is_exposed or not hidden:
      data['set'] = card.SET
      data['number'] = card.NUMBER
      data['name'] = card.NAME
    return data

  def serialize_remote(self, server, hidden=False):
    return {
        'name': str(server),
        'installed': [self.serialize_card(c, hidden=hidden)
                      for c in server.installed.cards],
        'ice': [self.serialize_card(c, hidden=hidden)
                for c in server.ice.cards],
        'cards': [],  # centrals only
        'game_id': server.game_id,
    }

  def serialize_central(self, server, shuffle=False,
                        hidden=False, card_count=False):
    if card_count:
      cards = [{} for c in server.cards]
    else:
      if shuffle:
        cards = [self.serialize_minimal(c, hidden=hidden) for c in
                 sorted(server.cards, key=lambda x: (x.SET, x.NUMBER))]
      else:
        cards = [self.serialize_card(c, hidden=hidden) for c in server.cards]

    return {
        'name': str(server),
        'cards': cards,
        'ice': [self.serialize_card(c, hidden=hidden)
                for c in server.ice.cards],
        'installed': [self.serialize_card(c, hidden=hidden)
                      for c in server.installed.cards],
        'game_id': server.game_id,
    }

