from typing import Optional, Any

import requests
import shapely
from environs import Env
from geopy import Point

from geopy.distance import distance
from pydantic import BaseModel
from pyproj import Geod
from shapely import LineString

env = Env()
env.read_env()
GEO_CODER_APIKEY = env('GEO_CODER_APIKEY')

MKAD_POLYGON = (
    Point(55.774558, 37.842762),
    Point(55.76522, 37.842789),
    Point(55.755723, 37.842627),
    Point(55.747399, 37.841828),
    Point(55.739103, 37.841217),
    Point(55.730482, 37.840175),
    Point(55.721939, 37.83916),
    Point(55.712203, 37.837121),
    Point(55.703048, 37.83262),
    Point(55.694287, 37.829512),
    Point(55.68529, 37.831353),
    Point(55.675945, 37.834605),
    Point(55.667752, 37.837597),
    Point(55.658667, 37.839348),
    Point(55.650053, 37.833842),
    Point(55.643713, 37.824787),
    Point(55.637347, 37.814564),
    Point(55.62913, 37.802473),
    Point(55.623758, 37.794235),
    Point(55.617713, 37.781928),
    Point(55.611755, 37.771139),
    Point(55.604956, 37.758725),
    Point(55.599677, 37.747945),
    Point(55.594143, 37.734785),
    Point(55.589234, 37.723062),
    Point(55.583983, 37.709425),
    Point(55.578834, 37.696256),
    Point(55.574019, 37.683167),
    Point(55.571999, 37.668911),
    Point(55.573093, 37.647765),
    Point(55.573928, 37.633419),
    Point(55.574732, 37.616719),
    Point(55.575816, 37.60107),
    Point(55.5778, 37.586536),
    Point(55.581271, 37.571938),
    Point(55.585143, 37.555732),
    Point(55.587509, 37.545132),
    Point(55.5922, 37.526366),
    Point(55.594728, 37.516108),
    Point(55.60249, 37.502274),
    Point(55.609685, 37.49391),
    Point(55.617424, 37.484846),
    Point(55.625801, 37.474668),
    Point(55.630207, 37.469925),
    Point(55.641041, 37.456864),
    Point(55.648794, 37.448195),
    Point(55.654675, 37.441125),
    Point(55.660424, 37.434424),
    Point(55.670701, 37.42598),
    Point(55.67994, 37.418712),
    Point(55.686873, 37.414868),
    Point(55.695697, 37.407528),
    Point(55.702805, 37.397952),
    Point(55.709657, 37.388969),
    Point(55.718273, 37.383283),
    Point(55.728581, 37.378369),
    Point(55.735201, 37.374991),
    Point(55.744789, 37.370248),
    Point(55.75435, 37.369188),
    Point(55.762936, 37.369053),
    Point(55.771444, 37.369619),
    Point(55.779722, 37.369853),
    Point(55.789542, 37.372943),
    Point(55.79723, 37.379824),
    Point(55.805796, 37.386876),
    Point(55.814629, 37.390397),
    Point(55.823606, 37.393236),
    Point(55.83251, 37.395275),
    Point(55.840376, 37.394709),
    Point(55.850141, 37.393056),
    Point(55.858801, 37.397314),
    Point(55.867051, 37.405588),
    Point(55.872703, 37.416601),
    Point(55.877041, 37.429429),
    Point(55.881091, 37.443596),
    Point(55.882828, 37.459065),
    Point(55.884625, 37.473096),
    Point(55.888897, 37.48861),
    Point(55.894232, 37.5016),
    Point(55.899578, 37.513206),
    Point(55.90526, 37.527597),
    Point(55.907687, 37.543443),
    Point(55.909388, 37.559577),
    Point(55.910907, 37.575531),
    Point(55.909257, 37.590344),
    Point(55.905472, 37.604637),
    Point(55.901637, 37.619603),
    Point(55.898533, 37.635961),
    Point(55.896973, 37.647648),
    Point(55.895449, 37.667878),
    Point(55.894868, 37.681721),
    Point(55.893884, 37.698807),
    Point(55.889094, 37.712363),
    Point(55.883555, 37.723636),
    Point(55.877501, 37.735791),
    Point(55.874698, 37.741261),
    Point(55.862464, 37.764519),
    Point(55.861979, 37.765992),
    Point(55.850257, 37.788216),
    Point(55.850383, 37.788522),
    Point(55.844167, 37.800586),
    Point(55.832707, 37.822819),
    Point(55.828789, 37.829754),
    Point(55.821072, 37.837148),
    Point(55.811599, 37.838926),
    Point(55.802781, 37.840004),
    Point(55.793991, 37.840965),
    Point(55.785017, 37.841576),
)


class GeoObject(BaseModel):
    address: str
    point: Optional[Point] = None
    is_in_mkad: Optional[bool] = None

    class Config:
        arbitrary_types_allowed = True

    def model_post_init(self, __context: Any) -> None:
        self.point = self._get_point(GEO_CODER_APIKEY)
        self.is_in_mkad = self._in_mkad()

    def _get_point(self, api_key) -> Point:
        base_url = 'https://geocode-maps.yandex.ru/1.x'
        response = requests.get(
            base_url,
            params={
                'geocode': self.address,
                'apikey': api_key,
                'format': 'json',
            }
        )
        response.raise_for_status()
        found_objects = response.json()['response']['GeoObjectCollection']['featureMember']

        if not found_objects:
            raise ObjectNotFound

        most_relevant, *_ = found_objects
        lon, lat = most_relevant['GeoObject']['Point']['pos'].split()
        return Point(lat, lon)

    def _in_mkad(self) -> bool:
        nodes = [
            shapely.geometry.Point(node.latitude, node.longitude)
            for node in MKAD_POLYGON
        ]
        polygon = shapely.geometry.Polygon(nodes)
        return polygon.contains(
            shapely.geometry.Point(self.point.latitude, self.point.longitude)
        )

    def get_distance_from_mkad(self) -> float:
        distances = [
            (node, distance(node, self.point))
            for node in MKAD_POLYGON
        ]
        closest = sorted(
            distances,
            key=lambda x: x[1],
        )[:2]

        # Немного школьной геометрии
        a = distance(closest[0][0], closest[1][0]).km
        b = closest[0][1].km
        c = closest[1][1].km
        if b ** 2 > (a ** 2 + c ** 2):
            return c
        elif c ** 2 > (a ** 2 + b ** 2):
            return b
        else:
            p = (a + b + c) / 2
            return 2 * ((p * (p - a) * (p - b) * (p - c)) ** 0.5) / a


class ObjectNotFound(Exception):
    pass
