from email.mime import base
from flask import Flask
from flask_session import Session
from os import environ
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

app = Flask(__name__)
db = SQLAlchemy()
jwt_manager = JWTManager()
session = Session()
mail = Mail()
login_manager = LoginManager(app)
login_manager.login_view = 'routes.login'

def init_app() -> Flask:
    # Based on the 'INSTANCE_MODE' environment variable, set the correct config
    env = environ.get('ENV')

    if env == 'dev':
        app.config.from_object('config.DevConfig')
    else:
        app.config.from_object('config.ProdConfig')
        
    from app.routes import base_endpoint
    from app.auth.routes import auth
    from app.errors.handlers import errors
    from app.projects.routes import projects

    app.register_blueprint(base_endpoint)
    app.register_blueprint(auth)
    app.register_blueprint(errors)
    app.register_blueprint(projects)
    
    db.init_app(app)
    with app.app_context():
        db.create_all()
    jwt_manager.init_app(app)
    session.init_app(app)
    login_manager.init_app(app)
    
    # Set up the SMTP connection for Gmail.
    app.config.update(
        MAIL_SERVER='smtp.gmail.com',
        MAIL_PORT=465,
        MAIL_USE_SSL=True,
        MAIL_USE_TLS=False,
        MAIL_USERNAME = app.config['EMAIL_USERNAME'],
        MAIL_PASSWORD = app.config['EMAIL_PASSWORD'],
        MAIL_DEBUG = False
    )
    app.testing = False
    
    mail.init_app(app)

    return app

def has_child_dict(dct: dict):
    for k in dct.keys():
        if isinstance(dct[k], list):
            return True
    return False

def get_type(obj):
    return type(obj)

app.jinja_env.globals.update(has_child_dict=has_child_dict)
app.jinja_env.globals.update(get_type=get_type)
    