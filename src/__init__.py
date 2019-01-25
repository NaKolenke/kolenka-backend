import os
import datetime
from flask import Flask
from flask_cors import CORS
from src.model import db
from src.auth import get_user_from_request
from src.utils import CustomJSONEncoder


def create_app():
    app = Flask(__name__)
    CORS(app)

    app.config.from_object('src.config.default.Config')
    app.config.from_envvar('KOLENKA_CONFIG', silent=True)
    
    app.json_encoder = CustomJSONEncoder

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    db.init_database(app)
    db.create_tables()

    @app.route("/")
    def motd():
        return "You are at the main page of kolenka api"

    from src.endpoints import users, tokens, doc, content, feedback, blogs, \
        posts

    app.register_blueprint(users.bp)
    app.register_blueprint(tokens.bp)
    app.register_blueprint(doc.bp)
    app.register_blueprint(content.bp)
    app.register_blueprint(feedback.bp)
    app.register_blueprint(blogs.bp)
    app.register_blueprint(posts.bp)

    @app.before_request
    def before_request():
        user = get_user_from_request()
        if user:
            user.last_active_date = datetime.datetime.now()
            user.save()

    return app
