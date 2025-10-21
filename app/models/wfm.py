from enum import Enum
from warframe_market.client import WarframeMarketClient
from warframe_market.common import Subtype

class ItemSubtype(Enum):
    CRAFTED = "crafted"
    BLUEPRINT = "blueprint"

class PriceCheck:
    """
    Utility class to check prices of items on Warframe Market
    """
    platinum = "<:Platinum:992917150358589550>"

    def __init__(self, item: str | None=None, client: WarframeMarketClient=None):
        self.client = client if isinstance(client, WarframeMarketClient) else WarframeMarketClient()
        self.item = item

    @property
    def slug(self):
        name = self.item.lower()
        if "-" in name:
            name = " ".join(name.split("-"))
        if "&" in name:
            name = name.replace("&","and")
        if "\'" in name:
            name = name.replace("\'","")

        return "_".join(name.split(" "))
    

    @classmethod
    def format_output(cls, orders: list[int|set[int,int]]) -> str:
        """
        Format the output of the price check.
        Supports both orders with just prices and orders with quantities.
        """
        if not orders:
            return "(N/A)"
        
        if isinstance(orders[0], int):
            return f"({', '.join([str(price) for price in orders])}){cls.platinum}"
        
        return " | ".join([f"{price}p × ({quantity})" for price,quantity in orders])

    
    async def check_raw(self,
        rank: int=0,
        charges: int=3,
        subtype: Subtype|None=None):
        """
        Check the raw price of an item, return a list with the prices
        """
        orders = await self.client.get_top_orders_for_item(
            slug=self.slug,
            rank=rank,
            charges=charges,
            subtype=subtype
        )
        orders = [order.platinum for order in orders.data.sell]

        if len(orders) == 0:
            return []
        
        return orders

    async def check(self,
        rank: int=0,
        charges: int=3,
        subtype: Subtype|None=None,
        ):
        orders = await self.client.get_top_orders_for_item(
            slug=self.slug,
            rank=rank,
            charges=charges,
            subtype=subtype
        )
        orders = [order.platinum for order in orders.data.sell]
        # if less than 5 orders, fill the rest with N/A
        # orders += ["N/A"] * (5 - len(orders))
        if len(orders) == 0:
            return "(N/A)"

        text = f"({", ".join([str(x) for x in orders])}){self.platinum}"
        return text

    async def check_with_quantity(self
        ,rank: int=0,
        charges: int=3,
        subtype: Subtype|None=None,
        ):

        orders = await self.client.get_top_orders_for_item(
            slug=self.slug,
            rank=rank,
            charges=charges,
            subtype=subtype
        )
        orders = [f"{order.platinum}p × ({order.quantity})" for order in orders.data.sell]
        # if less than 5 orders, fill the rest with N/A
        # orders += ["N/A"] * (5 - len(orders))
        if len(orders) == 0:
            return "N/A"

        text = f"{' | '.join([str(x) for x in orders])}"
        return text

    async def get_set_pieces(self):
        """
        Get all pieces of a set
        """
        item_set = await self.client.get_item_set(slug=self.slug)

        return {
            item.i18n["en"].name: {
                "slug": item.slug,
                "set": item.set_root,
                "quantity": item.quantity_in_set,
            }
            for item in item_set.data.items
        }
