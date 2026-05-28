from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class City:
    id: str
    name: str
    lat: float
    lon: float
    adm1: str = ""
    adm2: str = ""


@dataclass
class CurrentWeather:
    temp: int
    feels_like: int
    icon: str
    text: str
    wind_dir: str
    wind_scale: str
    wind_speed: int
    humidity: int
    precip: float
    pressure: int
    vis: int
    cloud: int
    dew: int
    update_time: str

    @property
    def summary(self) -> str:
        return f"{self.temp}°C {self.text}"


@dataclass
class ForecastDay:
    date: str
    temp_max: int
    temp_min: int
    icon_day: str
    text_day: str
    icon_night: str
    text_night: str
    wind_dir_day: str
    wind_scale_day: str
    wind_speed_day: int
    wind_dir_night: str
    wind_scale_night: str
    wind_speed_night: int
    humidity: int
    precip: float
    pressure: int
    uv_index: int
    vis: int


@dataclass
class AirQuality:
    aqi: int
    category: str
    primary: str
    pm2p5: float
    pm10: float
    no2: float
    so2: float
    co: float
    o3: float


@dataclass
class UVIndex:
    level: int
    category: str
    value: int
    text: str


@dataclass
class SunriseSunset:
    sunrise: str
    sunset: str


@dataclass
class WeatherData:
    city: City
    current: Optional[CurrentWeather] = None
    forecast: list[ForecastDay] = field(default_factory=list)
    yesterday: Optional[ForecastDay] = None
    air: Optional[AirQuality] = None
    sun: Optional[SunriseSunset] = None
    uv: Optional[UVIndex] = None


ICON_MAP = {
    "100": "☀️", "101": "🌤", "102": "⛅", "103": "🌥",
    "104": "☁️", "150": "🌙", "151": "🌤", "152": "🌤",
    "153": "🌤",
    "300": "🌧", "301": "🌧", "302": "🌧", "303": "🌧",
    "304": "🌧", "305": "🌧", "306": "🌧", "307": "🌧",
    "308": "🌧", "309": "🌧", "310": "🌧", "311": "🌧",
    "312": "🌧", "313": "🌧", "314": "🌧", "315": "🌧",
    "316": "🌧", "317": "🌧", "318": "🌧", "399": "🌧",
    "400": "🌨", "401": "🌨", "402": "🌨", "403": "🌨",
    "404": "🌨", "405": "🌨", "406": "🌨", "407": "🌨",
    "408": "🌨", "409": "🌨", "410": "🌨", "499": "🌨",
    "500": "🌫", "501": "🌫", "502": "🌫", "509": "🌫",
    "510": "🌫", "511": "🌫", "512": "🌫", "513": "🌫",
    "514": "🌫", "515": "🌫",
    "600": "🌬",
}

WIND_DIR_MAP = {
    "北": "N", "东北": "NE", "东": "E", "东南": "SE",
    "南": "S", "西南": "SW", "西": "W", "西北": "NW",
}


def get_icon(code: str) -> str:
    return ICON_MAP.get(code, "🌈")
