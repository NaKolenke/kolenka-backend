import os
from flask import Flask
app = Flask(__name__)
app.config.from_object('src.config.default.Config')
if ('KOLENKA_BACKEND_CONFIG' in os.environ):
    app.config.from_object('src.config.prod.Prod')

@app.route("/")
def hello():
    return "Hello World! "
