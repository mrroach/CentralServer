import json
import random
from csrv.model import parameters


def deserialize_response(game, data):
  response_class = getattr(parameters, data['response_type'])
  response = response_class()
  response.merge_from_dict(game, data['response_data'])
  return response


def render_choices(game, secret=False):
  phase = game.current_phase()
  data = {
      'phase': phase.__class__.__name__,
      'player': str(phase.player),
  }
  if not secret:
    choices = phase.choices()
    data['choices'] = [render_choice(c) for c in choices]
    data['null_ok'] = phase.NULL_OK
  return data

def serialize_choices(game, secret=False):
  data = render_choices(game, secret)
  return json.dumps(data)


def render_choice(choice):
  if choice.card:
    card = serialize_card(choice.card)
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

def serialize_game_corp(game):
  """Serialize the game state to json for the corp.

  Here "for the corp" means that the runner's hand and deck are not
  included (counts are given instead). And the identifiers for the cards
  in the corp's deck are given, but obviously not their position in the
  deck.
  """
  if game.run and game.run.server == game.corp.rnd:
    run_hidden = True
  else:
    run_hidden = False

  top_level = {
      'choice_count': game.choice_count,
      'corp_turn_count': game.corp_turn_count,
      'runner_turn_count': game.runner_turn_count,
      'active_player': str(game.active_player),
      'corp': serialize_corp(game.corp),
      'runner': serialize_runner(game.runner),
      'run': serialize_run(game.run, hidden=run_hidden),
      'choices': render_choices(
          game, game.current_phase().player != game.corp),
  }

  return json.dumps(top_level)


def serialize_game_runner(game):
  top_level = {
      'choice_count': game.choice_count,
      'corp_turn_count': game.corp_turn_count,
      'runner_turn_count': game.runner_turn_count,
      'active_player': str(game.active_player),
      'corp': serialize_corp(game.corp, hidden=True),
      'runner': serialize_runner(game.runner, hidden=False),
      'run': serialize_run(game.run),
      'choices': render_choices(
          game, game.current_phase().player != game.runner),
      }
  return json.dumps(top_level)


def serialize_run(run, hidden=False):
  if not run:
    return None
  if run.current_ice():
    ice = serialize_minimal(run.current_ice(), hidden=True)
  else:
    ice = None

  data = {
      'server': run.server.game_id,
      'current_ice': ice,
  }
  if hidden:
    data['accessed_cards'] = [{} for c in run.accessed_cards]
  else:
    data['accessed_cards'] = [serialize_card(c, hidden=hidden)
                              for c in run.accessed_cards]
  return data



def serialize_card(card, hidden=False):
  data = {
      'is_rezzed': card.is_rezzed,
      'is_faceup': card.is_faceup,
      'advancement_tokens': card.advancement_tokens,
      'credits': card.credits,
      'virus_counters': card.virus_counters,
      'game_id': card.game_id,
      'host': card.host.game_id if card.host else None,
      'hosted_cards': [c.game_id for c in card.hosted_cards],
  }

  if card.is_faceup or not hidden:
    data['set'] = card.SET
    data['number'] = card.NUMBER
    data['name'] = card.NAME
  return data


def serialize_minimal(card, hidden=False):
  data = {
      'game_id': card.game_id,
      'host': card.host.game_id if card.host else None,
  }
  if card.is_faceup or not hidden:
    data['set'] = card.SET
    data['number'] = card.NUMBER
    data['name'] = card.NAME
  return data


def serialize_remote(server, hidden=False):
  return {
      'name': str(server),
      'installed': [serialize_card(c, hidden=hidden)
                    for c in server.installed.cards],
      'ice': [serialize_card(c, hidden=hidden) for c in server.ice.cards],
      'cards': [],  # centrals only
      'game_id': server.game_id,
  }


def serialize_central(server, shuffle=False, hidden=False, card_count=False):
  if card_count:
    cards = [{} for c in server.cards]
  else:
    if shuffle:
      cards = [serialize_minimal(c, hidden=hidden) for c in
               sorted(server.cards, key=lambda x: (x.SET, x.NUMBER))]
    else:
      cards = [serialize_card(c, hidden=hidden) for c in server.cards]

  return {
      'name': str(server),
      'cards': cards,
      'ice': [serialize_card(c, hidden=hidden) for c in server.ice.cards],
      'installed': [serialize_card(c, hidden=hidden)
                    for c in server.installed.cards],
      'game_id': server.game_id,
  }


def serialize_corp(corp, hidden=False):

  return {
      'clicks': corp.clicks.value,
      'credits': corp.credits.value,
      'bad_publicity': corp.bad_publicity,
      'agenda_points': corp.agenda_points,
      'scored_agendas': [serialize_card(c) for c in corp.scored_agendas.cards],
      'identity': serialize_minimal(corp.identity),
      'hq': serialize_central(corp.hq, hidden=hidden, card_count=hidden),
      'archives': serialize_central(corp.archives, shuffle=True, hidden=hidden),
      'rnd': serialize_central(corp.rnd, shuffle=True, hidden=hidden,
                               card_count=hidden),
      'remotes': [serialize_remote(s, hidden=hidden) for s in corp.remotes],
  }


def serialize_runner(runner, hidden=False):
  # Sum all the general-purpose pools
  credits = sum([p.value for p in runner.find_pools()])

  return {
      'clicks': runner.clicks.value,
      'credits': credits,
      'agenda_points': runner.agenda_points,
      'brain_damage': runner.brain_damage,
      'tags': runner.tags,
      'scored_agendas': [serialize_card(c) for c in runner.scored_agendas.cards],
      'identity': serialize_minimal(runner.identity),
      'grip': [serialize_minimal(c, hidden=hidden) for c in runner.grip.cards],
      'heap': [serialize_minimal(c, hidden=hidden) for c in runner.heap.cards],
      'stack': [serialize_minimal(c, hidden=hidden) for c in
                sorted(runner.stack.cards, key=lambda x: (x.SET, x.NUMBER))],
      'rig': [serialize_card(c, hidden=hidden) for c in runner.rig.cards],
      'free_memory': runner.free_memory,
  }
