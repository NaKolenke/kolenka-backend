from flask import Flask
from src.model import db

def create_app():
    app = Flask(__name__)

    app.config.from_object('src.config.default.Config')
    app.config.from_envvar('KOLENKA_CONFIG', silent=True)

    db.init_database(app)
    db.create_tables()

    @app.route("/")
    def motd():
        return "You are at the main page of kolenka api"

    from src.endpoints import users
    from src.endpoints import tokens
    
    app.register_blueprint(users.bp)
    app.register_blueprint(tokens.bp)

    return app
