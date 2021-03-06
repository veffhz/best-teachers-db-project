from flask import Flask
from flask_migrate import Migrate

from config import Config

app = Flask(__name__)


def create_app(config_class=Config):
    app.config.from_object(config_class)
    from application import routes, forms
    from application.models import db
    db.init_app(app)
    migrate = Migrate()
    migrate.init_app(app, db)
    return app
