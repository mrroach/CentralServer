"""Parameters passed to an action/ability.

These represent targets for an action such as cards to trash duting install,
or cards to select for an operation.

They should be as general as possible so the client doesn't have to know too
many different request types. Some minimal enforcement can be done here, but
the action should do the heavy lifting for validation.
"""
import re
from csrv.model import errors
from csrv.model import game_object

VALID_FIELD_RE = re.compile(r'^[a-z][a-z_]+$')
NO_RESOLVE_FIELDS = set(['number', 'credits'])

class Response(object):
  def _resolve(self, game, field, val):
    if field in NO_RESOLVE_FIELDS:
      return val
    else:
      return game.get_game_object(val)

  def merge_from_dict(self, game, d):
    for key in d.keys():
      if VALID_FIELD_RE.match(key):
        var = getattr(self, key)
        if isinstance(var, list):
          for val in d[key]:
            var.append(self._resolve(game, key, val))
        else:
          setattr(self, key, self._resolve(game, key, d[key]))


class Request(game_object.GameObject):

  def __init__(self, game, card=None):
    game_object.GameObject.__init__(self, game)
    self.card = card

  def new_response(self):
    return self.RESPONSE_CLASS()

  def valid_response_options(self):
    return {}


class NullResponse(Response):

  def __bool__(self):
    return False


class NullRequest(Request):
  RESPONSE_CLASS = NullResponse


class InstallIceResponse(Response):

  def __init__(self):
    self.server = None
    self.ice_to_trash = []


class InstallIceRequest(Request):
  RESPONSE_CLASS = InstallIceResponse


class InstallProgramResponse(Response):

  def __init__(self):
    self.programs_to_trash = []
    self.host = None


class InstallProgramRequest(Request):
  RESPONSE_CLASS = InstallProgramResponse

  def valid_response_options(self):
    hosts = self.card.install_host_targets()
    programs_to_trash = self.card.install_programs_to_trash_targets()

    return {
        'host': [h.game_id for h in hosts],
        'programs_to_trash': [p.game_id for p in programs_to_trash],
    }


class InstallHardwareResponse(Response):

  def __init__(self):
    self.host = None


class InstallHardwareRequest(Request):
  RESPONSE_CLASS = InstallHardwareResponse

  def valid_response_options(self):
    hosts = self.card.install_host_targets()
    return {
        'host': [h.game_id for h in hosts],
    }


class InstallResourceResponse(Response):
  pass


class InstallResourceRequest(Request):
  RESPONSE_CLASS = InstallResourceResponse


class InstallAgendaAssetUpgradeResponse(Response):

  def __init__(self):
    self.server = None
    self.cards_to_trash = []


class InstallAgendaAssetUpgradeRequest(Request):
  RESPONSE_CLASS = InstallAgendaAssetUpgradeResponse


class InstallAgendaAssetResponse(InstallAgendaAssetUpgradeResponse):
  pass


class InstallAgendaAssetRequest(InstallAgendaAssetUpgradeRequest):
  RESPONSE_CLASS = InstallAgendaAssetResponse


class InstallUpgradeResponse(InstallAgendaAssetUpgradeResponse):
  pass


class InstallUpgradeRequest(InstallAgendaAssetUpgradeRequest):
  RESPONSE_CLASS = InstallUpgradeResponse


class PaymentSourceResponse(object):

  def __init__(self):
    self.pools = {}

  def add_payment(self, pool, amt):
    self.pools[pool] = amt

  def sources_match(self, appropriations):
    for pool in self.pools.keys():
      if not pool.appropriations & appropriations:
        return False
    return True

  def amount(self):
    return sum(self.pool.values())


class PaymentSourceRequest(object):
  response_class = PaymentSourceResponse

  def __init__(self, amt, appropriations):
    self.amt = amt
    self.appropriations = appropriations

  def handle_response(self, response):
    # TODO(mrroach): make this type check into a decorator
    if not isinstance(self.response_class, response):
      raise errors.InvalidResponseType()
    if (response.amount() == self.amt and
        response.sources_match(self.appropriations)):
      self.response = response
    else:
      raise errors.InvalidResponse()


class TargetAdvanceableCardsOperationResponse(object):
  pass


class TargetAdvanceableCardsOperationRequest(object):

  response_class = TargetAdvanceableCardsOperationResponse

  def __init__(self, cost, appropriations, num_cards):
    self.payment_source_request = PaymentSourceRequest(cost)
    self.target_advanceable_cards_request = TargetAdvanceableCardsRequest(
        num_cards)

  def handle_response(self, response):
    self.payment_source_request.handle_response(
        response.payment_source_response)
    self.target_advanceable_cards_request.handle_response(
        response.target_advanceable_cards_response)


class TargetInstalledAssetAgendaUpgradeRequest(object):
  pass


class TargetInstalledIceRequest(object):
  pass


class TargetInstalledCorpCardResponse(Response):
  def __init__(self):
    Response.__init__(self)
    self.card = None


class TargetInstalledCorpCardRequest(Request):
  RESPONSE_CLASS = TargetInstalledCorpCardResponse


class TargetServerResponse(Response):
  def __init__(self):
    Response.__init__(self)
    self.server = None


class TargetServerRequest(Request):
  RESPONSE_CLASS = TargetServerResponse


class StackCardResponse(Response):
  def __init__(self):
    Response.__init__(self)
    self.card = None
    self.cards = []


class StackCardRequest(Request):
  """A request for cards from the runners"""
  RESPONSE_CLASS = StackCardResponse

  def __init__(self, game, card=None, max_cards=1, min_cards=1):
    Request.__init__(self, game, card)
    self.max_cards = max_cards
    self.min_cards = min_cards


class ArchivesCardsResponse(Response):
  def __init__(self):
    Response.__init__(self)
    self.cards = []


class ArchivesCardsRequest(Request):
  RESPONSE_CLASS = ArchivesCardsResponse


class RndCardsResponse(Response):
  def __init__(self):
    Response.__init__(self)
    self.cards = []


class RndCardsRequest(Request):
  RESPONSE_CLASS = RndCardsResponse


class HqCardsResponse(Response):
  def __init__(self):
    Response.__init__(self)
    self.cards = []


class HqCardsRequest(Request):
  RESPONSE_CLASS = HqCardsResponse


class HeapCardsResponse(Response):
  def __init__(self):
    Response.__init__(self)
    self.cards = []


class HeapCardsRequest(Request):
  RESPONSE_CLASS = HeapCardsResponse


class ForfeitAgendaResponse(Response):
  def __init__(self):
    Response.__init__(self)
    self.agenda = None


class ForfeitAgendaRequest(Request):
  RESPONSE_CLASS = ForfeitAgendaResponse

  def valid_response_options(self):
    agendas = self.card.forfeit_agenda_targets()

    return {
        'agendas': [a.game_id for a in agendas],
    }


class NumericChoiceResponse(Response):
  def __init__(self):
    Response.__init__(self)
    self.number = 0


class NumericChoiceRequest(Request):
  RESPONSE_CLASS = NumericChoiceResponse


class VariableCreditCostResponse(Response):
  def __init__(self):
    Response.__init__(self)
    self.credits = 0


class VariableCreditCostRequest(Request):
  RESPONSE_CLASS = VariableCreditCostResponse


class ArrangeCardsResponse(Response):
  def __init__(self):
    Response.__init__(self)
    self.cards = []


class ArrangeCardsRequest(Request):
  RESPONSE_CLASS = ArrangeCardsResponse

  def __init__(self, game, cards=None):
    Request.__init__(self, game)
    self.cards = cards

  def valid_response_options(self):
    return {'cards': [c.game_id for c in self.cards]}

