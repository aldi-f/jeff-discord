######################################################
## Daily Sortie
######################################################
from msgspec import Struct, field
from datetime import datetime
from pytz import UTC

from app.redis_manager import cache
from app.funcs import find_internal_mission_name, find_internal_mission_type


def parse_mongo_date(date_dict: dict) -> datetime:
    """Parse MongoDB $date format to datetime."""
    number_long = date_dict["$date"]["$numberLong"]
    timestamp_ms = int(number_long)
    return datetime.fromtimestamp(timestamp_ms / 1000, tz=UTC)


class _Variant(Struct):
    mission_type: str = field(name="missionType")
    modifier_type: str = field(name="modifierType")
    node: str = field(name="node")
    tileset: str = field(name="tileset")

    def __post_init__(self):
        if isinstance(self.mission_type, str):
            self.mission_type = find_internal_mission_type(self.mission_type, cache) or self.mission_type
        if isinstance(self.node, str):
            self.node = find_internal_mission_name(self.node, cache) or self.node

class Sortie(Struct):
    activation: datetime | dict = field(name="Activation")
    expiry: datetime | dict = field(name="Expiry")
    reward: str = field(name="Reward")
    seed: int = field(name="Seed")
    boss: str = field(name="Boss")
    extra_drops: list = field(name="ExtraDrops")
    variants: list[_Variant] = field(name="Variants")
    twitter: bool = field(name="Twitter", default=False)

    def __post_init__(self):
        if isinstance(self.activation, dict):
            self.activation = parse_mongo_date(self.activation)
        if isinstance(self.expiry, dict):
            self.expiry = parse_mongo_date(self.expiry)

######################################################
#   "Sorties": [
#     {
#       "_id": {
#         "$oid": "68f3b5fe678e829e4889b041"
#       },
#       "Activation": {
#         "$date": {
#           "$numberLong": "1760803200000"
#         }
#       },
#       "Expiry": {
#         "$date": {
#           "$numberLong": "1760889600000"
#         }
#       },
#       "Reward": "/Lotus/Types/Game/MissionDecks/SortieRewards",
#       "Seed": 90866,
#       "Boss": "SORTIE_BOSS_HEK",
#       "ExtraDrops": [],
#       "Variants": [
#         {
#           "missionType": "MT_SURVIVAL",
#           "modifierType": "SORTIE_MODIFIER_BOW_ONLY",
#           "node": "SolNode15",
#           "tileset": "GrineerGalleonTileset"
#         },
#         {
#           "missionType": "MT_MOBILE_DEFENSE",
#           "modifierType": "SORTIE_MODIFIER_FREEZE",
#           "node": "SolNode30",
#           "tileset": "GrineerSettlementTileset"
#         },
#         {
#           "missionType": "MT_INTEL",
#           "modifierType": "SORTIE_MODIFIER_ARMOR",
#           "node": "SolNode746",
#           "tileset": "GrineerFortressTileset"
#         }
#       ],
#       "Twitter": true
#     }
#   ],