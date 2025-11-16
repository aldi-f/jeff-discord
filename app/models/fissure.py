######################################################
## Fissures
######################################################
from msgspec import Struct, field
from datetime import datetime
from pytz import UTC

from app.redis_manager import cache
from app.funcs import find_internal_mission_name

def parse_mongo_date(date_dict: dict) -> datetime:
    """Parse MongoDB $date format to datetime."""
    number_long = date_dict["$date"]["$numberLong"]
    timestamp_ms = int(number_long)
    return datetime.fromtimestamp(timestamp_ms / 1000, tz=UTC)


class Fissure(Struct):
    activation: datetime | dict = field(name="Activation")
    expiry: datetime | dict = field(name="Expiry")
    region: int = field(name="Region")
    seed: int = field(name="Seed")
    node: str = field(name="Node")
    mission_type: str = field(name="MissionType")
    modifier: str = field(name="Modifier")
    hard: bool = field(name="Hard", default=False)

    def __post_init__(self):
        if isinstance(self.activation, dict):
            self.activation = parse_mongo_date(self.activation)
        if isinstance(self.expiry, dict):
            self.expiry = parse_mongo_date(self.expiry)
        
        self.node = find_internal_mission_name(self.node, cache) or self.node
        

######################################################
#   "ActiveMissions": [
#     {
#       "_id": {
#         "$oid": "68f4e2b2304e5289c489b03e"
#       },
#       "Region": 18,
#       "Seed": 69163,
#       "Activation": {
#         "$date": {
#           "$numberLong": "1760879282779"
#         }
#       },
#       "Expiry": {
#         "$date": {
#           "$numberLong": "1760886424219"
#         }
#       },
#       "Node": "SolNode309",
#       "MissionType": "MT_SURVIVAL",
#       "Modifier": "VoidT6",
#       "Hard": true
#     },
#     {
#       "_id": {
#         "$oid": "68f4e636bfc721fe4f89b040"
#       },
#       "Region": 19,
#       "Seed": 3070,
#       "Activation": {
#         "$date": {
#           "$numberLong": "1760880182711"
#         }
#       },
#       "Expiry": {
#         "$date": {
#           "$numberLong": "1760887162945"
#         }
#       },
#       "Node": "SolNode747",
#       "MissionType": "MT_INTEL",
#       "Modifier": "VoidT5",
#       "Hard": true
#     },
#     {
#       "_id": {
#         "$oid": "68f4ebd739fff4db9789b03e"
#       },
#       "Region": 5,
#       "Seed": 43731,
#       "Activation": {
#         "$date": {
#           "$numberLong": "1760881623126"
#         }
#       },
#       "Expiry": {
#         "$date": {
#           "$numberLong": "1760886900706"
#         }
#       },
#       "Node": "SolNode74",
#       "MissionType": "MT_MOBILE_DEFENSE",
#       "Modifier": "VoidT2"
#     },
#     {
#       "_id": {
#         "$oid": "68f4ebd739fff4db9789b03f"
#       },
#       "Region": 10,
#       "Seed": 42576,
#       "Activation": {
#         "$date": {
#           "$numberLong": "1760881623126"
#         }
#       },
#       "Expiry": {
#         "$date": {
#           "$numberLong": "1760888261442"
#         }
#       },
#       "Node": "SolNode146",
#       "MissionType": "MT_SURVIVAL",
#       "Modifier": "VoidT2"
#     },