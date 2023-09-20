import pytest
from environs import Env
from flask import Flask, g

from . import address_checker

app = Flask(__name__)
app.register_blueprint(address_checker, url_prefix='/check')
client = app.test_client()
env = Env()
env.read_env()

success_cases = [
    ({'address': 'Обводное шоссе, 10, посёлок Рублёво, Москва, 121500'}, 0.7, False),
    ({'address': 'проспект Ленина, 82к3, Балашиха, Московская область'}, 9.2, False),
    ({'address': 'Нижний Новгород, ул. Полтавская, д. 30'}, 389, False),
    ({'address': 'Зелёный проспект, 20, Москва, 111397'}, None, True),
    ({'address': 'МКАД, 64-й километр, 20с4, Москва, 123458'}, None, True),
]

error_cases = [
    ({'address': ''},),
    ({'address': 'asdfasdf'},),
    ({'adres': 'Самара'},),
]


@pytest.mark.parametrize('data, distance, is_in_mkad,', success_cases)
def test_check_success(data: dict, distance: float, is_in_mkad: bool):
    url = '/check/'
    with app.app_context():
        g.geocoder_api_key = env('GEO_CODER_APIKEY')
        response = client.post(url, json=data)

    assert response.status_code == 200

    json_ = response.json

    if distance is not None:
        assert (distance * 0.95) < json_['data']['distance'] < (distance * 1.05)
    else:
        assert json_['data']['distance'] is None

    assert json_['data']['is_in_mkad'] == is_in_mkad
    assert json_['success'] is True


@pytest.mark.parametrize('data', error_cases)
def test_check_errors(data: dict):
    url = '/check/'
    with app.app_context():
        g.geocoder_api_key = env('GEO_CODER_APIKEY')
        response = client.post(url, json=data)

    assert response.status_code == 400

    json_ = response.json
    assert json_['success'] is False
    assert isinstance(json_['error'], str)
