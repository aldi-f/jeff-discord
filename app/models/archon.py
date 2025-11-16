######################################################
## Weekly Archon Hunt / Sportie
######################################################
from msgspec import Struct, field
from datetime import datetime
from pytz import UTC

from app.redis_manager import cache
from app.funcs import find_internal_mission_name, find_internal_name, find_internal_mission_type

def parse_mongo_date(date_dict: dict) -> datetime:
    """Parse MongoDB $date format to datetime."""
    number_long = date_dict["$date"]["$numberLong"]
    timestamp_ms = int(number_long)
    return datetime.fromtimestamp(timestamp_ms / 1000, tz=UTC)


def parse_unique_name(internal_name: str) -> str | None:
    """Try to parse internal name to user-friendly name."""

    # Try with raw name:
    name = find_internal_name(internal_name, cache)
    if name:
        return name
    
    # Try removing prefix
    internal_name = internal_name.replace("StoreItems/", "")
    name = find_internal_name(internal_name, cache)
    if name:
        return name
    
    return None


class _Mission(Struct):
    mission_type: str = field(name="missionType")
    node: str = field(name="node")

    def __post_init__(self):
        if isinstance(self.mission_type, str):
            self.mission_type = find_internal_mission_type(self.mission_type, cache) or self.mission_type
        if isinstance(self.node, str):
            self.node = find_internal_mission_name(self.node, cache) or self.node

class ArchonHunt(Struct):
    activation: datetime | dict = field(name="Activation")
    expiry: datetime | dict = field(name="Expiry")
    reward: str = field(name="Reward")
    seed: int = field(name="Seed")
    boss: str = field(name="Boss")
    missions: list[_Mission] = field(name="Missions")

    def __post_init__(self):
        if isinstance(self.activation, dict):
            self.activation = parse_mongo_date(self.activation)
        if isinstance(self.expiry, dict):
            self.expiry = parse_mongo_date(self.expiry)



######################################################
#   "LiteSorties": [
#     {
#       "_id": {
#         "$oid": "68ec3d7e53ab6c397989b03e"
#       },
#       "Activation": {
#         "$date": {
#           "$numberLong": "1760313600000"
#         }
#       },
#       "Expiry": {
#         "$date": {
#           "$numberLong": "1760918400000"
#         }
#       },
#       "Reward": "/Lotus/Types/Game/MissionDecks/ArchonSortieRewards",
#       "Seed": 14133,
#       "Boss": "SORTIE_BOSS_NIRA",
#       "Missions": [
#         {
#           "missionType": "MT_MOBILE_DEFENSE",
#           "node": "SolNode125"
#         },
#         {
#           "missionType": "MT_ARTIFACT",
#           "node": "SolNode100"
#         },
#         {
#           "missionType": "MT_ASSASSINATION",
#           "node": "SolNode53"
#         }
#       ]
#     }
#   ],