"""Constants for healthbox3."""
from logging import Logger, getLogger
from datetime import timedelta
from decimal import Decimal

LOGGER: Logger = getLogger(__package__)

NAME = "Healthbox 3"
DOMAIN = "healthbox3"
VERSION = "0.0.1"
MANUFACTURER = "Renson"
ATTRIBUTION = ""
SCAN_INTERVAL = timedelta(seconds=5)

SERVICE_START_ROOM_BOOST = "start_room_boost"
SERVICE_STOP_ROOM_BOOST = "stop_room_boost"


class Healthbox3RoomBoost:
    """Healthbox 3 Room Boost object."""

    level: float
    enabled: bool
    remaining: int

    def __init__(
        self, level: float = 100, enabled: bool = False, remaining: int = 900
    ) -> None:
        """Initialize the HB3 Room Boost."""
        self.level = level
        self.enabled = enabled
        self.remaining = remaining


class Healthbox3Room:
    """Healthbox 3 Room object."""

    boost: Healthbox3RoomBoost = None

    def __init__(self, room_id: int, room_data: object) -> None:
        """Initialize the HB3 Room."""
        self.room_id: int = room_id
        self.name: str = room_data["name"]
        self.type: str = room_data["type"]
        self.sensors_data: list = room_data["sensor"]

    @property
    def indoor_temperature(self) -> Decimal:
        """HB3 Indoor Temperature."""
        return [
            sensor["parameter"]["temperature"]["value"]
            for sensor in self.sensors_data
            if "temperature" in sensor["parameter"]
        ][0]

    @property
    def indoor_humidity(self) -> Decimal:
        """HB3 Indoor Humidity."""
        return [
            sensor["parameter"]["humidity"]["value"]
            for sensor in self.sensors_data
            if "humidity" in sensor["parameter"]
        ][0]

    @property
    def indoor_co2_concentration(self) -> Decimal | None:
        """HB3 Indoor CO2 Concentration."""
        co2_concentration = None
        try:
            co2_concentration = [
                sensor["parameter"]["concentration"]["value"]
                for sensor in self.sensors_data
                if "concentration" in sensor["parameter"]
            ][0]
        except IndexError:
            co2_concentration = None
        return co2_concentration

    @property
    def indoor_aqi(self) -> Decimal | None:
        """HB3 Indoor Air Quality Index."""
        aqi = None
        try:
            aqi = [
                sensor["parameter"]["index"]["value"]
                for sensor in self.sensors_data
                if "index" in sensor["parameter"]
            ][0]
        except IndexError:
            aqi = None
        return aqi


class Healthbox3DataObject:
    """Healthbox3 Data Object."""

    serial: str
    description: str
    warranty_number: str

    global_aqi: float = None

    rooms: list[Healthbox3Room]

    def __init__(self, data: any) -> None:
        """Initialize."""
        self.serial = data["serial"]
        self.description = data["description"]
        self.warranty_number = data["warranty_number"]

        self.global_aqi = self._get_global_aqi_from_data(data)

        hb3_rooms: list[Healthbox3Room] = []
        for room in data["room"]:
            hb3_room = Healthbox3Room(room, data["room"][room])
            hb3_rooms.append(hb3_room)

        self.rooms = hb3_rooms

    def _get_global_aqi_from_data(self, data: any) -> float | None:
        """Set Global AQI from Data Object"""
        sensors = data["sensor"]
        for sensor in sensors:
            if sensor["type"] == "global air quality index":
                return sensor["parameter"]["index"]["value"]
        return None
