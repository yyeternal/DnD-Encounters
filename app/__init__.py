from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config
from flask_moment import Moment
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager
# from flask_session import Session
from werkzeug.middleware.proxy_fix import ProxyFix


db = SQLAlchemy()
migrate = Migrate()
moment = Moment()
login_manager = LoginManager()

def create_app(config_class = Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.static_folder = config_class.STATIC_FOLDER
    app.template_folder = config_class.TEMPLATE_FOLDER_MAIN
    app.template_folder = config_class.TEMPLATE_FOLDER_AUTH
    #Session(app)

    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)


    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    migrate.init_app(app, db)
    moment.init_app(app)

    from app.main.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # register blueprints

    from app.main import main_blueprint as main
    from app.auth import auth_blueprint as auth 
    app.register_blueprint(auth, url_prefix='/auth')
    main.template_folder = Config.TEMPLATE_FOLDER_MAIN
    auth.template_folder = Config.TEMPLATE_FOLDER_AUTH
    app.register_blueprint(main)

    from app.errors import error_blueprint as errors
    errors.template_folder = Config.TEMPLATE_FOLDER_ERRORS
    app.register_blueprint(errors)

    csrf = CSRFProtect(app)
    return app