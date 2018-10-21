import os
from flask import Flask
from src.endpoints import users
from src.model import db

def create_app():
    app = Flask(__name__)

    app.register_blueprint(users.bp)

    app.config.from_object('src.config.default.Config')
    if ('KOLENKA_BACKEND_CONFIG' in os.environ):
        app.config.from_object('src.config.prod.Prod')

    db.init_database()
    db.create_tables()

    return app

app = create_app()

@app.route("/")
def hello():
    return "Testing update"
