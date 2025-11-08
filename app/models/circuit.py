######################################################
## Circuit
######################################################
import re
from datetime import datetime, timedelta

from msgspec import Struct, field
from pytz import UTC


class Circuit(Struct):
    category: str = field(name="Category")
    choices: list[str] = field(name="Choices")

    def __post_init__(self):
        self.choices = [
            re.sub(r"([a-z])([A-Z])", r"\1 \2", choice) for choice in self.choices
        ]

    @property
    def activation(self) -> datetime:
        """Start of week"""
        current_day = datetime.now().weekday()
        start_of_week = datetime.now() - timedelta(days=current_day)
        return start_of_week.replace(
            hour=0, minute=0, second=0, microsecond=0, tzinfo=UTC
        )

    @property
    def expiry(self) -> datetime:
        """End of week"""
        current_day = datetime.now().weekday()
        end_of_week = datetime.now() + timedelta(days=7 - current_day)
        return end_of_week.replace(
            hour=0, minute=0, second=0, microsecond=0, tzinfo=UTC
        )


######################################################
# "EndlessXpChoices": [
#   {
#     "Category": "EXC_NORMAL",
#     "Choices": [
#       "Garuda",
#       "Baruuk",
#       "Hildryn"
#     ]
#   },
#   {
#     "Category": "EXC_HARD",
#     "Choices": [
#       "Dera",
#       "Cestra",
#       "Okina",
#       "Sybaris",
#       "Sicarus"
#     ]
#   }
# ],
