######################################################
## Baro inventory
######################################################
from msgspec import Struct, field
from datetime import datetime
from pytz import UTC


def parse_mongo_date(date_dict: dict) -> datetime:
    """Parse MongoDB $date format to datetime."""
    number_long = date_dict["$date"]["$numberLong"]
    timestamp_ms = int(number_long)
    return datetime.fromtimestamp(timestamp_ms / 1000, tz=UTC)


class _Inventory(Struct):
    item_type: str = field(name="ItemType")
    ducats: int = field(name="PrimePrice", default=0)
    credits: int = field(name="RegularPrice", default=0)
    limit: int = field(name="Limit", default=0)


class Baro(Struct):
    activation: datetime | dict = field(name="Activation")
    expiry: datetime | dict = field(name="Expiry")
    character: str = field(name="Character")
    node: str = field(name="Node")
    manifest: list[_Inventory] = field(name="Manifest", default_factory=list)

    def __post_init__(self):
        if isinstance(self.activation, dict):
            self.activation = parse_mongo_date(self.activation)
        if isinstance(self.expiry, dict):
            self.expiry = parse_mongo_date(self.expiry)


##########################################################
# "VoidTraders": [
#   {
#     "_id": {
#       "$oid": "5d1e07a0a38e4a4fdd7cefca"
#     },
#     "Activation": {
#       "$date": {
#         "$numberLong": "1761915600000"
#       }
#     },
#     "Expiry": {
#       "$date": {
#         "$numberLong": "1762088400000"
#       }
#     },
#     "Character": "EvilBaroWeek3",
#     "Node": "EarthHUB",
#     "Manifest": [
#       {
#         "ItemType": "/Lotus/StoreItems/Upgrades/Skins/Armor/CrpHighArmor/EvilBaroArcaArmorC",
#         "PrimePrice": 196,
#         "RegularPrice": 294000
#       },
#       {
#         "ItemType": "/Lotus/StoreItems/Upgrades/Skins/Armor/CrpHighArmor/EvilBaroArcaArmorA",
#         "PrimePrice": 109,
#         "RegularPrice": 278000
#       },
#       {
#         "ItemType": "/Lotus/StoreItems/Upgrades/Skins/Armor/CrpHighArmor/EvilBaroArcaArmorL",
#         "PrimePrice": 184,
#         "RegularPrice": 251000
#       },
#       {
#         "ItemType": "/Lotus/StoreItems/Upgrades/Skins/Effects/BaroEvilEphemera",
#         "PrimePrice": 69,
#         "RegularPrice": 109000
#       },
#       {
#         "ItemType": "/Lotus/StoreItems/Upgrades/Skins/Weapons/Grimoire/GrimoireEvilBaroSkin",
#         "PrimePrice": 227,
#         "RegularPrice": 302000
#       },
#       {
#         "ItemType": "/Lotus/StoreItems/Upgrades/Skins/VoidTrader/EvilBaroSilvaAndAegis",
#         "PrimePrice": 132,
#         "RegularPrice": 298000
#       },
#       {
#         "ItemType": "/Lotus/StoreItems/Upgrades/Mods/Melee/DualStat/ElectEventMeleeMod",
#         "PrimePrice": 300,
#         "RegularPrice": 150000
#       },
#       {
#         "ItemType": "/Lotus/StoreItems/Upgrades/Mods/Rifle/Expert/WeaponRecoilReductionModExpert",
#         "PrimePrice": 300,
#         "RegularPrice": 220000
#       },
#       {
#         "ItemType": "/Lotus/StoreItems/Types/BoosterPacks/BaroTreasureBox",
#         "PrimePrice": 0,
#         "RegularPrice": 50000,
#         "Limit": 1
#       },
