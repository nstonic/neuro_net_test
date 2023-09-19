from flask import Flask

from distance_checker import address_checker

app = Flask(__name__)
app.register_blueprint(address_checker, url_prefix='/check')

