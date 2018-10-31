import os
from flask import Flask
from src.model import db

def create_app():
    app = Flask(__name__)

    app.config.from_object('src.config.default.Config')
    if ('KOLENKA_CONFIG' in os.environ):
        app.config.from_object(os.environ['KOLENKA_CONFIG'])

    db.init_database(app)
    db.create_tables()

    @app.route("/")
    def motd():
        return "You are at the main page of kolenka api"

    from src.endpoints import users
    app.register_blueprint(users.bp)

    return app
