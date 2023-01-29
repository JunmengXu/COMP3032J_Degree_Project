from flask import Flask
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from config import config
from flask_migrate import Migrate

db=SQLAlchemy()
bootstrap=Bootstrap()
#synchronization_update@1

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    db.init_app(app)
    bootstrap.init_app(app)

    with app.app_context():
        db.create_all()

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    from .errors import not_found,internal_server_error
    app.register_error_handler(404,not_found) #synchronization_update@2 (app/errors.py)
    app.register_error_handler(500,internal_server_error) #synchronization_update@3 (app/errors.py)

    return app

