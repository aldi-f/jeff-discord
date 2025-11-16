######################################################
## Darvo's daily deal
######################################################
from msgspec import Struct, field
from datetime import datetime
from pytz import UTC

from app.redis_manager import cache
from app.funcs import find_internal_weapon_name, find_internal_warframe_name, find_internal_name


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
        if isinstance(self.store_item, str):
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