import os
from flask import Flask
import flask_resize
from flask_babel import Babel
from flask_uploads import (UploadSet, configure_uploads, IMAGES)

from importlib import import_module

from sqlalchemy.engine import Engine 
from sqlalchemy import event

from paddelranking.website.config import Config, FlaskUploadConfig, FlaskResizeConfig

babel = Babel()

photos = UploadSet('photos', IMAGES)
portraits = UploadSet('portraits', IMAGES)

basedir = os.path.abspath(os.path.dirname(__file__))
def register_blueprints(app):
    for module_name in ('users',):
        module = import_module('paddelranking.website.{}.routes'.format(module_name))
        app.register_blueprint(module.blueprint)

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='change-your-secret',
        SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(app.instance_path, 'paddelranking.sqlite'),
        SQLALCHEMY_TRACK_MODIFICATIONS = False
    )

    app.config.from_object(Config)
    
    # Database models
    from .models import (db, migrate, User, Team, login_manager,
                         Player, Tournament, Round, Match, MatchResultsByTeam,
                         )
    db.init_app(app)
    migrate.init_app(app, db)

    # Flask Resize
    app.config.from_object(FlaskResizeConfig)
    resize = flask_resize.Resize(app)

    # Flask Babel, i18n
    babel.init_app(app)

    # Flask Login
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    # Bootstap 3
    from flask_bootstrap import Bootstrap
    bootstrap = Bootstrap(app)


    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Front Page
    from . import frontpage
    app.register_blueprint(frontpage.bp)
    app.add_url_rule('/', endpoint='index')

    @app.shell_context_processor
    def make_shell_context():
        return {'db': db, 'User': User, 'Team': Team,
                'Player': Player, 'Tournament': Tournament,
                'Round': Round, 'Match': Match, 'MatchResultsByTeam':MatchResultsByTeam}

    # Auth BluePrint
    from . import auth
    app.register_blueprint(auth.bp)

    # New BluePrints Implementation
    register_blueprints(app)

    # Upload images settings
    app.config.from_object(FlaskUploadConfig)
    photos = UploadSet('photos', IMAGES)
    portraits = UploadSet('portraits', IMAGES)

    configure_uploads(app, (photos, portraits))

    with app.app_context():
        from . import filtros
    return app
