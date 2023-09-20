import logging

from flask import Blueprint, request
from geopy.exc import GeopyError
from pydantic import ValidationError

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
    data = {
        'success': False,
        'error': None,
        'data': {}
    }

    try:
        point = GeoObject.model_validate(input_json)
    except ValidationError:
        data['error'] = 'JSON is not valid'
        return data, 400
    except ObjectNotFound:
        data['error'] = "Object doesn't exist in this world"
        return data, 400
    except GeopyError:
        data['error'] = 'GeoCoder error'
        return data, 415

    if point.is_in_mkad:
        distance = None
        logging.debug(f'Проверка адреса: {point.address}. Находится внутри МКАД')
    else:
        distance = point.get_distance_from_mkad()
        logging.debug(f'Проверка адреса: {point.address}. Расстояние до МКАД: {distance:.2f} км')

    data.update({
        'success': True,
        'data': {
            'address': point.address,
            'is_in_mkad': point.is_in_mkad,
            'distance': distance,
        }
    })
    return data
