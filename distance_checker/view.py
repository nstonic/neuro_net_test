import logging

from flask import Blueprint, request
from pydantic import ValidationError
from requests import HTTPError

from .geo_service import ObjectNotFound, GeoObject

logging.basicConfig(
    filename='distance_checker_log.log',
    filemode='a',
    format='%(asctime)s %(message)s',
    datefmt='%d.%m.%Y %H:%M:%S',
    level=logging.DEBUG
)

address_checker = Blueprint('distance_from_mkad', __name__)


@address_checker.route('/', methods=['POST'])
def check():
    input_json = request.get_json()

    try:
        point = GeoObject.model_validate(input_json)
    except ValidationError:
        return {"success": False, "error": "JSON is not valid"}, 400
    except ObjectNotFound:
        return {"success": False, "error": "Object is not exists in this world"}, 400
    except HTTPError:
        return {"success": False, "error": "GeoCoder error"}, 415

    if point.is_in_mkad:
        distance = None
        logging.debug(f'Проверка адреса: {point.address}. Находится внутри МКАД')
    else:
        distance = point.get_distance_from_mkad()
        logging.debug(f'Проверка адреса: {point.address}. Расстояние до МКАД: {distance:.2f} км')

    return {"success": True, "is_in_mkad": point.is_in_mkad, "distance": distance}
