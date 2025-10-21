######################################################
## Fissures
######################################################
from msgspec import Struct, field
from datetime import datetime
from pytz import UTC


def parse_mongo_date(date_dict: dict) -> datetime:
    """Parse MongoDB $date format to datetime."""
    number_long = date_dict["$date"]["$numberLong"]
    timestamp_ms = int(number_long)
    return datetime.fromtimestamp(timestamp_ms / 1000, tz=UTC)


class _ActiveChallenge(Struct):
    activation: datetime | dict = field(name="Activation")
    expiry: datetime | dict = field(name="Expiry")
    challenge: str = field(name="Challenge")

    def __post_init__(self):
        if isinstance(self.activation, dict):
            self.activation = parse_mongo_date(self.activation)
        if isinstance(self.expiry, dict):
            self.expiry = parse_mongo_date(self.expiry)

    @property
    def type(self) -> str:
        if self.challenge.startswith("/Lotus/Types/Challenges/Seasons/Daily/"):
            return "Daily"
        elif self.challenge.startswith("/Lotus/Types/Challenges/Seasons/Weekly/"):
            return "Weekly"
        elif self.challenge.startswith("/Lotus/Types/Challenges/Seasons/WeeklyHard/"):
            return "Weekly Hard"
        else:
            return "Unknown"
    
    @property
    def standing(self) -> int:
        if self.type == "Daily":
            return 1000
        elif self.type == "Weekly":
            return 4500
        elif self.type == "Weekly Hard":
            return 7000
        else:
            return 0

class Nightwave(Struct):
    activation: datetime | dict = field(name="Activation")
    expiry: datetime | dict = field(name="Expiry")
    affiliation_tag: str = field(name="AffiliationTag")
    season: int = field(name="Season")
    phase: int = field(name="Phase")
    params: str = field(name="Params")
    active_challenges: list[_ActiveChallenge] = field(name="ActiveChallenges")

    def __post_init__(self):
        if isinstance(self.activation, dict):
            self.activation = parse_mongo_date(self.activation)
        if isinstance(self.expiry, dict):
            self.expiry = parse_mongo_date(self.expiry)


######################################################
#   "SeasonInfo": {
#     "Activation": {
#       "$date": {
#         "$numberLong": "1747851300000"
#       }
#     },
#     "Expiry": {
#       "$date": {
#         "$numberLong": "1761588000000"
#       }
#     },
#     "AffiliationTag": "RadioLegionIntermission13Syndicate",
#     "Season": 15,
#     "Phase": 0,
#     "Params": "",
#     "ActiveChallenges": [
#       {
#         "_id": {
#           "$oid": "001600220000000000000306"
#         },
#         "Daily": true,
#         "Activation": {
#           "$date": {
#             "$numberLong": "1760659200000"
#           }
#         },
#         "Expiry": {
#           "$date": {
#             "$numberLong": "1760918400000"
#           }
#         },
#         "Challenge": "/Lotus/Types/Challenges/Seasons/Daily/SeasonDailyAimGlide"
#       },
#       {
#         "_id": {
#           "$oid": "001600220000000000000298"
#         },
#         "Activation": {
#           "$date": {
#             "$numberLong": "1760313600000"
#           }
#         },
#         "Expiry": {
#           "$date": {
#             "$numberLong": "1760918400000"
#           }
#         },
#         "Challenge": "/Lotus/Types/Challenges/Seasons/Weekly/SeasonWeeklyCompleteMobileDefense"
#       },
#       {
#         "_id": {
#           "$oid": "001600220000000000000301"
#         },
#         "Activation": {
#           "$date": {
#             "$numberLong": "1760313600000"
#           }
#         },
#         "Expiry": {
#           "$date": {
#             "$numberLong": "1760918400000"
#           }
#         },
#         "Challenge": "/Lotus/Types/Challenges/Seasons/WeeklyHard/SeasonWeeklyHardEliteBeastSlayer"
#       }
#     ]
#   },