import time
from datetime import datetime, timedelta

import httpx
import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519, rsa, ec

from config import get_project_id, get_credential_id, get_api_host, read_private_key
from weather_app.models import (
    AirQuality,
    City,
    CurrentWeather,
    ForecastDay,
    SunriseSunset,
    WeatherData,
)

WEATHER_CODE_MAP = {
    "100": "晴", "101": "多云", "102": "少云", "103": "晴间多云",
    "104": "阴", "300": "阵雨", "301": "强阵雨", "302": "雷阵雨",
    "303": "强雷阵雨", "304": "雷阵雨伴有冰雹",
    "305": "小雨", "306": "中雨", "307": "大雨", "308": "极端降雨",
    "309": "毛毛雨/细雨", "310": "暴雨", "311": "大暴雨",
    "312": "特大暴雨", "313": "冻雨", "314": "小到中雨",
    "315": "中到大雨", "316": "大到暴雨", "317": "暴雨到大暴雨",
    "318": "大暴雨到特大暴雨",
    "399": "雨",
    "400": "小雪", "401": "中雪", "402": "大雪", "403": "暴雪",
    "404": "雨夹雪", "405": "雨雪天气", "406": "阵雨夹雪",
    "407": "阵雪", "408": "小到中雪", "409": "中到大雪",
    "410": "大到暴雪", "499": "雪",
    "500": "薄雾", "501": "雾", "502": "霾", "503": "扬沙",
    "504": "浮尘", "507": "沙尘暴", "508": "强沙尘暴",
    "509": "浓雾", "510": "强浓雾", "511": "中度霾",
    "512": "重度霾", "513": "严重霾", "514": "大雾",
    "515": "特强浓雾",
    "600": "热",
}


class ApiError(Exception):
    pass


class QWeatherClient:
    def __init__(self):
        self._project_id = get_project_id()
        self._credential_id = get_credential_id()
        self._host = get_api_host()
        self._client = httpx.Client(timeout=10)
        self._token: str | None = None
        self._token_exp: float = 0

        pem_data = read_private_key()
        if pem_data:
            self._priv_key_obj = serialization.load_pem_private_key(
                pem_data.encode() if isinstance(pem_data, str) else pem_data,
                password=None,
            )
            if isinstance(self._priv_key_obj, ed25519.Ed25519PrivateKey):
                self._jwt_alg = "EdDSA"
            elif isinstance(self._priv_key_obj, rsa.RSAPrivateKey):
                self._jwt_alg = "RS256"
            elif isinstance(self._priv_key_obj, ec.EllipticCurvePrivateKey):
                self._jwt_alg = "ES256"
            else:
                raise ApiError(f"Unsupported key type: {type(self._priv_key_obj).__name__}")
        else:
            self._priv_key_obj = None
            self._jwt_alg = None

    def _build_url(self, path: str) -> str:
        return f"https://{self._host}{path}"

    def _ensure_token(self):
        now = time.time()
        if self._token and now < self._token_exp - 30:
            return
        payload = {
            "sub": self._project_id,
            "iat": int(now) - 30,
            "exp": int(now) + 900,
        }
        headers = {"kid": self._credential_id}
        self._token = jwt.encode(
            payload, self._priv_key_obj, algorithm=self._jwt_alg, headers=headers
        )
        self._token_exp = payload["exp"]

    def _get(self, url: str, params: dict | None = None, check_code: bool = True) -> dict:
        self._ensure_token()
        resp = self._client.get(
            url,
            params=params,
            headers={"Authorization": f"Bearer {self._token}"},
        )
        resp.raise_for_status()
        data = resp.json()
        if check_code and data.get("code") != "200":
            msg = data.get("code", "unknown")
            raise ApiError(f"API error code: {msg} from {url}")
        return data

    def lookup_city(self, query: str) -> list[City]:
        data = self._get(self._build_url("/geo/v2/city/lookup"), {"location": query})
        results = []
        for loc in data.get("location", []):
            results.append(
                City(
                    id=loc["id"],
                    name=loc["name"],
                    lat=float(loc["lat"]),
                    lon=float(loc["lon"]),
                    adm1=loc.get("adm1", ""),
                    adm2=loc.get("adm2", ""),
                )
            )
        return results

    def fetch_weather(self, city: City) -> WeatherData:
        wd = WeatherData(city=city)

        now_data = self._get(self._build_url("/v7/weather/now"), {"location": city.id})
        now = now_data.get("now", {})
        if now:
            wd.current = CurrentWeather(
                temp=int(now.get("temp", 0)),
                feels_like=int(now.get("feelsLike", 0)),
                icon=now.get("icon", ""),
                text=WEATHER_CODE_MAP.get(now.get("icon", ""), now.get("text", "")),
                wind_dir=now.get("windDir", ""),
                wind_speed=int(now.get("windSpeed", 0)),
                humidity=int(now.get("humidity", 0)),
                precip=float(now.get("precip", 0)),
                pressure=int(now.get("pressure", 0)),
                vis=now.get("vis", "0"),
                cloud=int(now.get("cloud", 0)),
                dew=now.get("dew", "0"),
                update_time=now_data.get("updateTime", ""),
            )

        fc_data = self._get(self._build_url("/v7/weather/7d"), {"location": city.id})
        for day in fc_data.get("daily", []):
            wd.forecast.append(
                ForecastDay(
                    date=day.get("fxDate", ""),
                    temp_max=int(day.get("tempMax", 0)),
                    temp_min=int(day.get("tempMin", 0)),
                    icon_day=day.get("iconDay", ""),
                    text_day=WEATHER_CODE_MAP.get(
                        day.get("iconDay", ""), day.get("textDay", "")
                    ),
                    icon_night=day.get("iconNight", ""),
                    text_night=WEATHER_CODE_MAP.get(
                        day.get("iconNight", ""), day.get("textNight", "")
                    ),
                    wind_dir_day=day.get("windDirDay", ""),
                    wind_speed_day=int(day.get("windSpeedDay", 0)),
                    wind_dir_night=day.get("windDirNight", ""),
                    wind_speed_night=int(day.get("windSpeedNight", 0)),
                    humidity=int(day.get("humidity", 0)),
                    precip=float(day.get("precip", 0)),
                    pressure=int(day.get("pressure", 0)),
                    uv_index=int(day.get("uvIndex", 0)),
                    vis=day.get("vis", "0"),
                )
            )

        try:
            yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")
            hist = self._get(
                self._build_url("/v7/historical/weather"),
                {"location": city.id, "date": yesterday},
            )
            daily = hist.get("weatherDaily", {})
            hourly_list = hist.get("weatherHourly", [])
            icon = hourly_list[0].get("icon", "") if hourly_list else ""
            wd.yesterday = ForecastDay(
                date=daily.get("date", ""),
                temp_max=int(daily.get("tempMax", 0)),
                temp_min=int(daily.get("tempMin", 0)),
                icon_day=icon,
                text_day=WEATHER_CODE_MAP.get(icon, ""),
                humidity=int(daily.get("humidity", 0)),
                precip=float(daily.get("precip", 0)),
                pressure=int(daily.get("pressure", 0)),
                icon_night="", text_night="",
                wind_dir_day="", wind_speed_day=0,
                wind_dir_night="", wind_speed_night=0,
                uv_index=0, vis="0",
            )
        except Exception:
            wd.yesterday = None

        air_data = self._get(
            self._build_url(f"/airquality/v1/current/{city.lat}/{city.lon}"),
            check_code=False,
        )
        if air_data:
            indexes = air_data.get("indexes", [])
            pollutants = air_data.get("pollutants", [])
            idx = next((i for i in indexes if i.get("code") == "us-epa"), indexes[0] if indexes else None)
            pol_map = {p["code"]: p["concentration"]["value"] for p in pollutants if "concentration" in p}
            wd.air = AirQuality(
                aqi=int(idx["aqi"]) if idx else 0,
                category=idx.get("category", "") if idx else "",
                primary=(idx.get("primaryPollutant") or {}).get("name", "") if idx else "",
                pm2p5=pol_map.get("pm2p5", 0),
                pm10=pol_map.get("pm10", 0),
                no2=pol_map.get("no2", 0),
                so2=pol_map.get("so2", 0),
                co=pol_map.get("co", 0),
                o3=pol_map.get("o3", 0),
            )

        try:
            today = datetime.now().strftime("%Y%m%d")
            sun_data = self._get(
                self._build_url("/v7/astronomy/sun"),
                {"location": city.id, "date": today},
            )
            wd.sun = SunriseSunset(
                sunrise=sun_data.get("sunrise", ""),
                sunset=sun_data.get("sunset", ""),
            )
        except Exception:
            wd.sun = None

        return wd

    def close(self):
        self._client.close()
