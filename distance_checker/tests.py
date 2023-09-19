import pytest

from main import app

success_cases = [
    ({'address': 'Обводное шоссе, 10, посёлок Рублёво, Москва, 121500'}, 0.66, False),
    ({'address': 'проспект Ленина, 82к3, Балашиха, Московская область'}, 9.2, False),
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
    client = app.test_client()
    url = '/check/'
    response = client.post(url, json=data)

    assert response.status_code == 200

    json_ = response.json

    if distance is not None:
        assert (distance * 0.90) < json_['distance'] < (distance * 1.10)
    else:
        assert json_['distance'] is None

    assert json_['is_in_mkad'] == is_in_mkad
    assert json_['success'] is True


@pytest.mark.parametrize('data', error_cases)
def test_check_errors(data: dict):
    client = app.test_client()
    url = '/check/'
    response = client.post(url, json=data)

    assert response.status_code == 400

    json_ = response.json
    assert json_['success'] is False
