from msgspec import Struct, field

from app.models.darvo import Darvo
from app.models.archon import ArchonHunt
from app.models.sortie import Sortie
from app.models.fissure import Fissure
from app.models.nightwave import Nightwave


class WorldstateModel(Struct):
    version: int = field(name="Version")
    mobile_version: str = field(name="MobileVersion")
    build_label: str = field(name="BuildLabel")
    time: int = field(name="Time")

    # Darvo deals
    daily_deals: list[Darvo] = field(name="DailyDeals")

    # Archon hunt:
    lite_sorties: list[ArchonHunt] = field(name="LiteSorties")

    # Sortie
    sorties: list[Sortie] = field(name="Sorties")

    # Fissures
    active_missions: list[Fissure] = field(name="ActiveMissions")

    # Nightwave
    season_info: Nightwave = field(name="SeasonInfo")