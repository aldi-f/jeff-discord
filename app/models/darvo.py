######################################################
## Darvo's daily deal
######################################################
from msgspec import Struct, field
from datetime import datetime
from pytz import UTC


def parse_mongo_date(date_dict: dict) -> datetime:
    """Parse MongoDB $date format to datetime."""
    number_long = date_dict["$date"]["$numberLong"]
    timestamp_ms = int(number_long)
    return datetime.fromtimestamp(timestamp_ms / 1000, tz=UTC)


class DailyDeal(Struct):
    store_item: str = field(name="StoreItem")
    activation: datetime = field(name="Activation")
    expiry: datetime = field(name="Expiry")
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