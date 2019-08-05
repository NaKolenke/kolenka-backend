import os
import datetime
import subprocess
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
        return "You are at the main page of kolenka api." +\
            "Current version is " + get_app_version()

    from src.endpoints import users, tokens, doc, content, feedback, blogs, \
        posts, tags, notifications, stickers, search, pages

    app.register_blueprint(users.bp)
    app.register_blueprint(tokens.bp)
    app.register_blueprint(doc.bp)
    app.register_blueprint(content.bp)
    app.register_blueprint(feedback.bp)
    app.register_blueprint(blogs.bp)
    app.register_blueprint(posts.bp)
    app.register_blueprint(tags.bp)
    app.register_blueprint(notifications.bp)
    app.register_blueprint(stickers.bp)
    app.register_blueprint(search.bp)
    app.register_blueprint(pages.bp)

    @app.before_request
    def before_request():
        user = get_user_from_request()
        if user:
            user.last_active_date = datetime.datetime.now()
            user.save()

    return app


def get_app_version():
    command = 'git log --tags --simplify-by-decoration --pretty="format:%d"' +\
                ' | grep "tag:" -m 1'
    tags = subprocess.run(command, stdout=subprocess.PIPE, shell=True)
    last_tags = tags.stdout.decode('utf-8')

    end = min(last_tags.find(','), last_tags.find(')'))
    return last_tags[5:end]
