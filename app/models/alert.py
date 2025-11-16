######################################################
## Alerts
######################################################
from msgspec import Struct, field
from datetime import datetime
from pytz import UTC

from app.redis_manager import cache
from app.funcs import find_internal_name, find_internal_mission_name, find_internal_mission_type


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


class _counted_items(Struct):
    item: str = field(name="ItemType")
    quantity: int = field(name="ItemCount")

    def __post_init__(self):
        if isinstance(self.item, str):
            self.item = parse_unique_name(self.item) or self.item


class _missionReward(Struct):
    credits: int = field(name="credits", default=0)
    counted_items: list[_counted_items] = field(
        name="countedItems", default_factory=list
    )


class _MissionInfo(Struct):
    location: str = field(name="location")
    mission_type: str = field(name="missionType")
    faction: str = field(name="faction")
    mission_reward: _missionReward = field(name="missionReward")
    difficulty: int = field(name="difficulty", default=0)
    min_level: int = field(name="minEnemyLevel", default=0)
    max_level: int = field(name="maxEnemyLevel", default=0)
    max_waves: int = field(name="maxWaveNum", default=0)

    def __post_init__(self):
        if isinstance(self.location, str):
            self.location = find_internal_mission_name(self.location, cache) or self.location
        if isinstance(self.mission_type, str):
            self.mission_type = find_internal_mission_type(self.mission_type, cache) or self.mission_type


class Alert(Struct):
    activation: datetime | dict = field(name="Activation")
    expiry: datetime | dict = field(name="Expiry")
    tag: str = field(name="Tag")
    mission_info: _MissionInfo = field(name="MissionInfo")

    def __post_init__(self):
        if isinstance(self.activation, dict):
            self.activation = parse_mongo_date(self.activation)
        if isinstance(self.expiry, dict):
            self.expiry = parse_mongo_date(self.expiry)


##########################################################
# "Alerts": [
#   {
#     "_id": {
#       "$oid": "6903d8e9726d2ae01b03aa0e"
#     },
#     "Activation": {
#       "$date": {
#         "$numberLong": "1761937200000"
#       }
#     },
#     "Expiry": {
#       "$date": {
#         "$numberLong": "1763146800000"
#       }
#     },
#     "MissionInfo": {
#       "location": "SolNode30",
#       "missionType": "MT_ARTIFACT",
#       "faction": "FC_GRINEER",
#       "difficulty": 1,
#       "missionReward": {
#         "credits": 10000,
#         "countedItems": [
#           {
#             "ItemType": "/Lotus/Types/Items/MiscItems/Forma",
#             "ItemCount": 3
#           }
#         ]
#       },
#       "levelOverride": "/Lotus/Levels/Proc/Grineer/GrineerSettlementDisruption",
#       "enemySpec": "/Lotus/Types/Game/EnemySpecs/GrineerSettlementSurvivalA",
#       "extraEnemySpec": "/Lotus/Types/Game/EnemySpecs/SpecialMissionSpecs/DisruptionGrineerGhouls",
#       "minEnemyLevel": 20,
#       "maxEnemyLevel": 30,
#       "descText": "/Lotus/Language/Alerts/TennoUnitedAlert",
#       "maxWaveNum": 8
#     },
#     "Tag": "LotusGift",
#     "ForceUnlock": true
#   }
