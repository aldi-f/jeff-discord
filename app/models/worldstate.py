from msgspec import Struct, field

from app.models.alert import Alert
from app.models.archon import ArchonHunt
from app.models.baro import Baro
from app.models.circuit import Circuit
from app.models.darvo import Darvo
from app.models.fissure import Fissure
from app.models.nightwave import Nightwave
from app.models.sortie import Sortie


class WorldstateModel(Struct, kw_only=True):
    version: int = field(name="Version")
    mobile_version: str = field(name="MobileVersion")
    build_label: str = field(name="BuildLabel")
    time: int = field(name="Time")

    # Alerts
    alerts: list[Alert] = field(name="Alerts", default_factory=list)

    # Archon hunt:
    lite_sorties: list[ArchonHunt] = field(name="LiteSorties")

    # Baro
    void_traders: list[Baro] = field(name="VoidTraders")

    # Circuit
    circuits: list[Circuit] = field(name="EndlessXpChoices")

    # Darvo deals
    daily_deals: list[Darvo] = field(name="DailyDeals")

    # Fissures
    active_missions: list[Fissure] = field(name="ActiveMissions")

    # Nightwave
    season_info: Nightwave = field(name="SeasonInfo")

    # Sortie
    sorties: list[Sortie] = field(name="Sorties")
