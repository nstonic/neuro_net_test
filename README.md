# Flask Blueprint для нахождения расстояния от МКАД до указанного адреса

## Как настроить

Установите зависимости:

```shell
pip install -r requirements.txt
```

Получите ключ разработчика [Яндекс API Геокодера](https://yandex.ru/dev/maps/geocoder/doc/desc/concepts/about.html) \
Задайте его в переменной окружения `GEO_CODER_APIKEY` \
При работе приложения ключ передаётся в контексте в переменной `g.geocoder_api_key`

```python
env = Env()
env.read_env()

with app.app_context():
    g.geocoder_api_key = env('GEO_CODER_APIKEY')
```

## Как запустить тесты

```shell
pytest .\distance_checker\tests.py
```

## Как использовать

Для проверки адреса отправьте `POST` запрос на присвоенный сервису url, например `/check/`. Адрес передаётся в json вида
`{'address': 'Мой дом'}`:

```python
response = requests.post('127.0.0.1:8080/check/', json={'address': 'Мой дом'})
```

Ответ приходит в виде json со следующей структурой:

```json
{
  "success": true,
  "error": null,
  "data": {
    "address": "Мой дом",
    "is_in_mkad": false,
    "distance": 10
  }
}
```

Дистанция рассчитывается в километрах. Данные сохраняются в файл `distance_checker_log.log`

### Возможные ошибки

- Не верный формат данных в запросе

```json
  "error": "JSON is not valid"
```

- Объект не найден на карте

```json
  "error": "Object doesn't exist in that world"
```

- Ошибка при обращении к Яндекс Геокодер

```json
  "error": "GeoCoder error"
```
