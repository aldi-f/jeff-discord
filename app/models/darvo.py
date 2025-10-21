######################################################
## Darvo's daily deal
######################################################
from msgspec import Struct, field
from datetime import datetime
from pytz import UTC

from app.redis_manager import cache
from app.funcs import find_internal_weapon_name, find_internal_warframe_name


def parse_mongo_date(date_dict: dict) -> datetime:
    """Parse MongoDB $date format to datetime."""
    number_long = date_dict["$date"]["$numberLong"]
    timestamp_ms = int(number_long)
    return datetime.fromtimestamp(timestamp_ms / 1000, tz=UTC)

def parse_unique_name(internal_name: str) -> str | None:
    """Try to parse internal name to user-friendly name."""
    name = internal_name.replace("StoreItems/", "")

    if name.startswith("/Lotus/Weapons/"):  # Weapon
        return find_internal_weapon_name(name, cache)
    elif name.startswith("/Lotus/Powersuits/"):  # Warframe
        return find_internal_warframe_name(name, cache)
    else:
        return None


class Darvo(Struct):
    activation: datetime | dict = field(name="Activation")
    expiry: datetime | dict = field(name="Expiry")
    store_item: str = field(name="StoreItem")
    discount: int = field(name="Discount")
    original_price: int = field(name="OriginalPrice")
    sale_price: int = field(name="SalePrice")
    amount_total: int = field(name="AmountTotal")
    amount_sold: int = field(name="AmountSold")

    def __post_init__(self):
        if isinstance(self.activation, dict):
            self.activation = parse_mongo_date(self.activation)
        if isinstance(self.expiry, dict):
            self.expiry = parse_mongo_date(self.expiry)

        # try to parse store_item to user-friendly name
        self.store_item = parse_unique_name(self.store_item) or self.store_item

######################################################
#   "DailyDeals": [
#     {
#       "StoreItem": "/Lotus/StoreItems/Weapons/Tenno/Melee/Dagger/Dagger",
#       "Activation": {
#         "$date": {
#           "$numberLong": "1760828400000"
#         }
#       },
#       "Expiry": {
#         "$date": {
#           "$numberLong": "1760922000000"
#         }
#       },
#       "Discount": 40,
#       "OriginalPrice": 75,
#       "SalePrice": 45,
#       "AmountTotal": 300,
#       "AmountSold": 59
#     }
#   ],