######################################################
## Weekly Archon Hunt / Sportie
######################################################
from msgspec import Struct, field
from datetime import datetime
from pytz import UTC


def parse_mongo_date(date_dict: dict) -> datetime:
    """Parse MongoDB $date format to datetime."""
    number_long = date_dict["$date"]["$numberLong"]
    timestamp_ms = int(number_long)
    return datetime.fromtimestamp(timestamp_ms / 1000, tz=UTC)


class _Mission(Struct):
    mission_type: str = field(name="missionType")
    node: str = field(name="node")

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