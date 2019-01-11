import datetime
from flask import Flask
from src.model import db
from src.auth import get_user_from_request

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
    from src.endpoints import doc
    
    app.register_blueprint(users.bp)
    app.register_blueprint(tokens.bp)
    app.register_blueprint(doc.bp)

    @app.before_request
    def before_request():
        user = get_user_from_request()
        if user:
            user.last_active_date = datetime.datetime.now()
            user.save()
    
    @app.after_request
    def after_request(response):
        response.headers['Content-Type'] = 'application/json; charset=utf-8'
        return response

    return app